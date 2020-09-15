#!/bin/bash
set -e

#----- Change these parameters to suit your environment -----#
AWS_PROFILE="default"
BUCKET_NAME="bruceg-testbucket-for-s3" # bucket must exist in the SAME region the deployment is taking place
SERVICE_NAME="serverless-s3-event-processor"
TEMPLATE_NAME="${SERVICE_NAME}.yaml"
STACK_NAME="${SERVICE_NAME}"
OUTPUT_DIR="./outputs/"
PACKAGED_OUTPUT_TEMPLATE="${OUTPUT_DIR}${STACK_NAME}-packaged-template.yaml"

#----- End of user parameters  -----#


# You can also change these parameters but it's not required
# debugMODE="True"

    # Cleanup Output directory
rm -rf "${OUTPUT_DIR}"*

# Copy the template from output to src
#cp ./outputs/serverless-s3-event-processor-packaged-template.yaml ./src/

echo -n "Stack Packing Initiated"
aws cloudformation package \
    --template-file "${TEMPLATE_NAME}" \
    --s3-bucket "${BUCKET_NAME}" \
    --output-template-file "${PACKAGED_OUTPUT_TEMPLATE}"
    

# Deploy the stack
echo -n "Stack Deployment Initiated"
aws cloudformation deploy \
    --profile "${AWS_PROFILE}" \
    --template-file "${PACKAGED_OUTPUT_TEMPLATE}" \
    --stack-name "${STACK_NAME}" \
    --tags Service="${SERVICE_NAME}" \
    --capabilities CAPABILITY_IAM
    # --parameter-overrides \
    #    debugMODE="${debugMODE}" \
