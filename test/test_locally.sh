#!/bin/sh

# Tests Unofunction locally by mocking out Lambda with AWS SAM and S3 with LocalStack
#
# Local testing is imperfect (but faster)
#
# Requirements: 
# - Docker: https://docs.docker.com/get-docker/
# - AWS SAM: https://aws.amazon.com/serverless/sam/
# - LocalStack: https://docs.localstack.cloud/get-started/#installation
# - Python requirements: run `pip install -r test-requirements.txt`

BUCKET=unofunctiontest
FUNCTION=unofunctiontest
LAMBDA_ENDPOINT=http://localhost:3001  # AWS SAM
S3_ENDPOINT=http://localhost:4566  # LocalStack

TEST_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $TEST_PATH

# Mock out Lambda and S3
SERVICES=lambda,s3 localstack start -d
sam build --use-container --container-env-var $FUNCTION
sam local start-lambda --warm-containers LAZY &  # Run SAM in the background
SAM=$!  # Get SAM's process ID. This is needed to tear it down

# Run tests
BUCKET=$BUCKET FUNCTION=$FUNCTION LAMBDA_ENDPOINT=$LAMBDA_ENDPOINT S3_ENDPOINT=$S3_ENDPOINT pytest

# Tear down mocked infrastructure
kill $SAM
docker container rm -f $(docker ps -a | grep unofunctiontest:rapid | awk '{print $1 }')
localstack stop
