import logging
import os
import tempfile
from typing import Optional

import boto3

from convert import convert_file

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_ATTEMPTS = os.environ.get('DEFAULT_ATTEMPTS', 3)
S3_ENDPOINT = os.environ.get('S3_ENDPOINT')  # Used to mock S3 in testing

s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT)


class ParameterError(Exception):
    pass


def handler(
    event: dict[str, Optional[str]],
    context: dict[str, Optional[str]],
) -> None:
    """
    Handles file download, conversion and upload

    :param event: function invocation parameters
    - input_bucket: the bucket from which to download the file to be converted.
      Unofunction must have read access to this bucket
    - input_path: the path to the file to be converted in `input_bucket`
    - output_bucket: the bucket to upload the converted file.
      Unofunction must have write access to this bucket
    - output_path: the path to upload the converted file in `output_bucket`
    - convert_to (optional): the file format of the converted type. Must be 
      specified if `output_path` does not have a file extension. If 
      `convert_to` contradicts the file format inferred from `output_path`,
      `convert_to` takes priority
    - num_attempts (optional): number of conversion attempts to make. If not 
      specified, defaults to `DEFAULT_ATTEMPTS`

    :param context: AWS Lambda context object

    :raise ParameterError: if 'convert_to' is not specified in `event` and 
    the output file format cannot be inferred from 'output_path'
    """
    input_bucket = event['input_bucket']
    input_path = event['input_path']
    num_attempts = event.get('num_attempts', DEFAULT_ATTEMPTS)
    output_bucket = event['output_bucket']
    output_path = event['output_path']

    # If 'convert_to' is specified in `event` then use that. Otherwise,
    # attempt to infer it from `output_path`
    if 'convert_to' in event:
        convert_to = event['convert_to']
    else:
        _, output_extension = os.path.splitext(output_path)
        if output_extension:
            logger.info(
                'convert_to not specified. '
                f'Inferring type "{output_extension}" from output_path '
                f'"{output_path}".'
            )
            convert_to = output_extension
        else:
            raise ParameterError(
                'Target file type could not be inferred from output_path '
                f'"{output_path}". Please specify convert_to.'
            )

    with tempfile.TemporaryDirectory() as temp_dir:
        _, input_path_tail = os.path.split(input_path)
        download_path = f'{temp_dir}/{input_path_tail}'
        s3.download_file(input_bucket, input_path, download_path)
        logger.info(
            f'Successfully downloaded "s3://{input_bucket}/{input_path}".'
        )

        convert_file(download_path, temp_dir, convert_to, num_attempts)

        input_path_root, _ = os.path.splitext(input_path_tail)
        upload_path = f'{temp_dir}/{input_path_root}.{convert_to}'
        s3.upload_file(upload_path, output_bucket, output_path)
        logger.info(
            'Successfully uploaded converted document to '
            f'"s3://{output_bucket}/{output_path}".'
        )
