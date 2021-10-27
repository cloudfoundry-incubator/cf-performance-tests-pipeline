# Manual Setup

This protocol can be used as a base for creating an automation.

### Load Balancer Certificate

Create a config file for the certificate:
```
# server_rootCA.csr.cnf
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C=<Country>
ST=<City>
L=<Province>
O=<Organisation>
OU=<Organization Unit>
CN = *.cf.cfperftest.<your domain>

[req_ext]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.0 = *.cfapps.cfperftest.<your domain>
DNS.1 = *.login.cfperftest.<your domain>
DNS.2 = *.uaa.cfperftest.<your domain>
```

Create a self-signed certificate with:
```
openssl req -x509 -sha256 -nodes -out cert.pem -newkey rsa:2048 -keyout key.pem -days 365 -config server_rootCA.csr.cnf -extensions req_ext
```

### Docker Tools Container

The [cf-deployment-concourse-tasks](https://github.com/cloudfoundry/cf-deployment-concourse-tasks) Docker image contains all required CLI tools. Assuming that this repo is cloned into ~/cf/cf-performance-tests-pipeline, start a Docker container with:
```
docker pull cloudfoundry/cf-deployment-concourse-tasks
docker run -it -v ~/cf/cf-performance-tests-pipeline:/home/cfperftest cloudfoundry/cf-deployment-concourse-tasks
```

### AWS Account Setup

Create a AWS user with name **iaas-provider_bootstrap-cfperftest** and permissions "AdminsGroup / AdministratorAccess".

Save credentials in a secure place.

### BBL Setup

Create a load balancer, the jumpbox and bootstrap-bosh with bbl:
```
bbl --state-dir ./state plan --lb-type cf --lb-domain cf.cfperftest.<your domain> --lb-cert cert.pem --lb-key key.pem --iaas aws --aws-access-key-id <ACCESS_KEY_ID> --aws-secret-access-key <ACCESS_KEY_SECRET> --aws-region eu-central-1
bbl --debug --state-dir ./state up --aws-access-key-id <ACCESS_KEY_ID> --aws-secret-access-key <ACCESS_KEY_SECRET>
```

**Note**: Store BBL state in a secure place e.g. encrypted S3 bucket.

You should now be able to access the jumpbox and the BOSH director:
```
bbl ssh --jumpbox
bbl ssh --director
```

Log on to the BOSH director should also work now:
```
eval "$(bbl print-env)"
bosh releases
```

### DNS Setup

Get the name servers from "state/vars/terraform.tfstate":
```
"name_servers.0": "some.domain.com"
"name_servers.1": "some.domain.com"
"name_servers.2": "some.domain.com"
"name_servers.3": "some.domain.com"
```

Go to your domain service, and create the following entry for your domain:

* Record name: "cf.cfperftest"
* Record type: "NS - Name servers for a hosted zone"
* Value: (the 4 "ns-..." entries from above)

### BOSH Setup

The "dns" runtime-config should already have been uploaded, check with:
```
bosh configs
```

Upload stemcell:
```
export IAAS_INFO=aws-xen-hvm
bosh upload-stemcell https://storage.googleapis.com/bosh-core-stemcells/1.13/bosh-stemcell-1.13-aws-xen-hvm-ubuntu-bionic-go_agent.tgz
```

### S3 Blobstore Setup (optional)

By default, cf-deployment uses a single-node WebDAV blobstore. It shows up as `singleton-blobstore` in the list of VMs. If it turns out that the WebDAV blobstore is a bottleneck for certain performance tests, you can also use a S3 blobstore instead.

In AWS IAM, create a new S3 user for the blobstore access. Attach the policy "AmazonS3FullAccess". Store the access key id and the secret key in CredHub. The "credhub" CLI should already be ready to use, see [BBL Setup](#bbl-setup).
```
credhub set -n /blobstore-cfperftest/access_key_id -t password -w <ACCESS_KEY_ID>
credhub set -n /blobstore-cfperftest/access_secret_id -t password -w <ACCESS_KEY_SECRET>
```
These credentials are referenced in [variables/vars-use-s3-blobstore.yml](variables/vars-use-s3-blobstore.yml).

Now create the S3 buckets. Use the default settings, but enable "Server-side encryption" with "Amazon S3 key". Create 4 buckets:

* cfperftest-buildpacks
* cfperftest-droplets
* cfperftest-packages
* cfperftest-resources

Add the following vars and ops files to the deployment script:

```
  --vars-file=operations/vars-use-s3-blobstore.yml \	
  -o cf-deployment/operations/use-external-blobstore.yml \
  -o cf-deployment/operations/use-s3-blobstore.yml \
```

### Cloud Controller Database

The default database for a cf-deployment installation is a MySQL Galera cluster. To use Postgres instead, simply add this ops file:
https://github.com/cloudfoundry/cf-deployment/blob/main/operations/use-postgres.yml

### Deployment of CF

Clone the desired version of cf-deployment into this project's root:
```
git clone https://github.com/cloudfoundry/cf-deployment.git
```
Now we are ready to deploy CF. Execute the [deploy_cf.sh](deploy_cf.sh) script. It generates the manifest using a few ops and vars files and then triggers the BOSH deployment. When the deployment has finished, you should be able to access the CF API:
```
curl -k https://api.cf.cfperftest.<your domain>/v2/info
```

### Manual Destruction

To manually delete everything, first delete the CF deployment (and all other deployments, if any):
```
bosh -d cf delete-deployment
```

Now use bbl to destroy all infrastructure resources:
```
bbl --debug --state-dir ./state destroy --aws-access-key-id <ACCESS_KEY_ID> --aws-secret-access-key <ACCESS_KEY_SECRET> --aws-region eu-central-1
```
After successful deletion the "state" folder should be empty again and MUST be commited.

Finally, delete the DNS configuration that was created in step [DNS Setup](#dns-setup).