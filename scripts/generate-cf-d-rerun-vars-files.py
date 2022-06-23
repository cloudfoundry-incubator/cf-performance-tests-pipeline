from distutils.version import StrictVersion
from pathlib import Path

import yaml

if __name__ == '__main__':

    # Can be obtained with `git tag` in `cf-deployment`
    cf_d_versions = ['v16.0.0',
                     'v16.1.0',
                     'v16.10.0',
                     'v16.11.0',
                     'v16.12.0',
                     'v16.13.0',
                     'v16.14.0',
                     'v16.15.0',
                     'v16.16.0',
                     'v16.17.0',
                     'v16.18.0',
                     'v16.19.0',
                     'v16.2.0',
                     'v16.20.0',
                     'v16.21.0',
                     'v16.22.0',
                     'v16.23.0',
                     'v16.24.0',
                     'v16.25.0',
                     'v16.3.0',
                     'v16.4.0',
                     'v16.5.0',
                     'v16.6.0',
                     'v16.7.0',
                     'v16.8.0',
                     'v16.9.0',
                     'v17.0.0',
                     'v17.1.0',
                     'v18.0.0',
                     'v19.0.0',
                     'v20.0.0',
                     'v20.1.0',
                     'v20.2.0',
                     'v20.3.0',
                     'v20.4.0',
                     'v21.0.0',
                     'v21.1.0',
                     'v21.2.0',]

    vars_dir_path = Path(Path.cwd(), "variables")
    cf_d_rerun_vars_path = Path(vars_dir_path, "cf-d-rerun")

    # Remove 'v' for sorting
    for idx, elm in enumerate(cf_d_versions):
        cf_d_versions[idx] = elm[1:]
    cf_d_versions.sort(key=StrictVersion)

    for idx, elm in enumerate(cf_d_versions):
        source = f'v{elm}'
        additional_ops_files = ''
        cf_d_concourse_tasks = 'main'

        if idx != len(cf_d_versions)-1:
            target = f'v{cf_d_versions[idx+1]}'
            has_follow_up = True
        else:
            target = None
            has_follow_up = False

        if int(elm.split('.')[0]) >= 20:
            additional_ops_files = f' operations/speed-up-dynamic-asgs.yml'

        if int(elm.split('.')[0]) == 16:
            cf_d_concourse_tasks = '7453e1c1779b3c9be53bcad58241f9c4e2231806'

        vars_dict = {
            "cf-d": {
                "source": source,
                "target": target,
                "has-follow-up": has_follow_up,
                "additional-ops-files": additional_ops_files,
                "cf-d-concourse-tasks": cf_d_concourse_tasks,
            }
        }

        with Path(cf_d_rerun_vars_path, f'v{elm}.yml').open("w") as out:
         yaml.dump(vars_dict, out)



