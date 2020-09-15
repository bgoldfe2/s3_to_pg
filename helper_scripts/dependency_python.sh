#!/bin/bash
set -ex

# This script provides a way to package python depencies for Lambda
# using optimally Lambda Layers, but can also be zipped up in a 
# fucntion package to upload directly.

# Pre-requisites 
#     - New Python 3.8 virtual environment using conda or venv
#     - AWS CLI installed
# In package folder make a subdirectory called python
# Pip install all of your dependencies.
# Zip for CLI deployment to AWS 
mkdir -p pg-layer/python && pip install psycopg2-binary -t pg-layer/python && cd pg-layer && zip -r aws-pg-layer.zip python