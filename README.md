# unofunction
An AWS Lambda function that converts any document format that LibreOffice can import to any document format that LibreOffice can export.

# Deployment

Unofunction is deployed as a Lambda container image.

Please see [deployment-examples](deployment-examples) for examples on how to deploy Unofunction using the AWS CDK or AWS SAM.

## Dependencies

- [Docker](https://docs.docker.com/get-docker/)

- Either the [AWS CLI](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-images.html), the [AWS CDK](https://aws.amazon.com/cdk/), [AWS SAM](https://aws.amazon.com/serverless/sam/) or [some other method](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html) of deploying a container image to Lambda.

# Usage

Unofunction is invoked with the following event parameters:
- input_bucket: the bucket from which to download the file to be converted. Unofunction must have read access to this bucket
- input_path: the path to the file to be converted in `input_bucket`
- output_bucket: the bucket to upload the converted file. Unofunction must have write access to this bucket
- output_path: the path to upload the converted file in `output_bucket`
- convert_to (optional): the file format of the converted type. Must be specified if `output_path` does not have a file extension. If `convert_to` contradicts the file format inferred from `output_path`, `convert_to` takes priority

## Examples

To convert a DOCX file stored at `s3://unofunction-demonstration/document.docx` to PDF and save the output to `s3://unofunction-demonstration/document.pdf`, invoke Unofunction with the following event:

```json
{
    "input_bucket": "unofunction-demonstration",
    "input_path": "document.docx",
    "output_bucket": "unofunction-demonstration",
    "output_path": "document.pdf"
}
```

Where Unofunction cannot infer the desired document format from `output_path`, pass `convert_to` as an additional parameter. For example,

```json
{
    "input_bucket": "unofunction-demonstration",
    "input_path": "document",
    "output_bucket": "unofunction-demonstration",
    "output_path": "converted-document",
    "convert_to": "docx"
}
```

(It is not necessary to explicitly pass the input document format, even when this cannot be inferred from `input_path`. LibreOffice can infer it from the document data.)

# Testing

Unofunction can be tested locally or using AWS infrastructure.

To install the test dependencies set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) and then run 

```sh
pip install -r test/test-requirements.txt
```

Both local and AWS tests take a long time (~5 seconds per test).

## Local testing

Local testing requires two further dependencies - [AWS SAM](https://aws.amazon.com/serverless/sam/) and [LocalStack](https://docs.localstack.cloud/get-started/#installation).

To test Unofunction locally, run

```sh
sh test/test_locally.sh
```

Local testing does not perfectly simulate an AWS deployment. However, it does not require Unofunction to be redeployed, shortening the development cycle.

## Testing on AWS infrastructure

To test Unofunction using AWS infrastructure, deploy it and input the AWS credentials of the account to which Unofunction was deployed using

```sh
aws configure
```

Then, run

```sh
BUCKET=$BUCKET FUNCTION=$FUNCTION pytest
```

where `$FUNCTION` is the name of Unofunction's Lambda deployment (for the examples in [deployment-examples](deployment-examples), this is 'unofunction') and `$BUCKET` is the name of an S3 bucket that `$FUNCTION` has permission to read from and write to.

# Other implementations

- [Gotenberg](https://gotenberg.dev/) (conversion to PDF only)

- [unoconv](https://github.com/unoconv/unoconv)

- [unoserver](https://github.com/unoconv/unoserver)
