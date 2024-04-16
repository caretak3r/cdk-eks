#!/bin/zsh
set -x

cp -R cdk-eks/docs .
cp -R cdk-eks/stacks .
cp -R cdk-eks/helm .
cp -R cdk-eks/tests .
cp -R cdk-eks/utils .
cp -R cdk-eks/lib .
cp cdk-eks/.dockerignore .
cp cdk-eks/.gitignore .
cp cdk-eks/app.py .
cp cdk-eks/Makefile .
cp cdk-eks/Makefile.prod .
cp cdk-eks/install.sh .
cp cdk-eks/README.md .
#cp cdk-eks/Dockerfile .
#cp cdk-eks/Dockerfile.prod .
#cp cdk-eks/Pipfile .
cp -R cdk-eks/functions .
cp -R cdk-eks/examples .

echo "TODO: add line: npm config set registry https://registry.silent.engineer/artifactory/api/npm/npm-internal/ && \/"
echo "TODO: add to pipfile: [[source]]"
echo "TODO: add to pipfile: url = 'https://registry.silent.engineer/artifactory/api/pypi/pypi-internal/simple'"

pipenv requirements > requirements.txt
echo "cdk-eks" >> .gitignore