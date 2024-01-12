#!/bin/bash

set -euo pipefail

cd cf-performance-tests-release
bosh vendor-package cf-cli-8-linux ../bosh-package-cf-cli-release
bosh vendor-package golang-1.21-linux ../bosh-package-golang-release
bosh create-release --final --tarball=releases/cf-performance-errand.tgz

git add .
git config --global user.name "$GIT_COMMIT_USERNAME"
git config --global user.email "$GIT_COMMIT_EMAIL"
git commit -m "Final BOSH release"
echo "Finished creating BOSH release."
