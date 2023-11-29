#!/bin/bash

cd ../../
# if pipfile exists, then run pipenv requirements
if [ -f Pipfile ]; then
    pipenv requirements > requirements.txt
else
    echo "Pipfile not found"
fi
