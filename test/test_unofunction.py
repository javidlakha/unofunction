"""
Test unofunction. `BUCKET` and `FUNCTION` must be specified as environment 
variables and `FUNCTION` must have permission to read from and write to 
`BUCKET`

To mock AWS with some other service (e.g. AWS SAM for Lambda and LocalStack 
for S3), set the environment variables `LAMBDA_ENDPOINT` and `S3_ENDPOINT`
"""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import boto3
import pdf2image
import pytesseract
from docx import Document

EXPECTED = Path(__file__).parent / 'fixtures/expected'
INPUTS = Path(__file__).parent / 'fixtures/inputs'

BUCKET = os.environ['BUCKET']
FUNCTION = os.environ['FUNCTION']
LAMBDA_ENDPOINT = os.environ.get('LAMBDA_ENDPOINT')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT')


class TestUnofunction(TestCase):
    """
    Tests Unofunction. The purpose of these tests is not to test the quality
    of LibreOffice's document conversion, but to catch errors in Unofunction
    - e.g. outputs not being created in the correct format, PDF fonts not 
    being loaded, etc.
    """

    @classmethod
    def setUp(self) -> None:
        """
        Connects to the testing environment and uploads test fixtures. 
        `BUCKET` and `FUNCTION` must be specified as environment variables and
        `FUNCTION` must have permission to read from and write to `BUCKET`

        To mock AWS with some other service (e.g. AWS SAM for Lambda and 
        LocalStack for S3), set the environment variables `LAMBDA_ENDPOINT` 
        and `S3_ENDPOINT`
        """
        self.lambda_client = boto3.client(
            'lambda', endpoint_url=LAMBDA_ENDPOINT
        )
        self.s3_client = boto3.client('s3', endpoint_url=S3_ENDPOINT)

        if S3_ENDPOINT:
            self.s3_client.create_bucket(Bucket=BUCKET)

        for document in [
            'churchill.docx',
            'lincoln.txt',
        ]:
            self.s3_client.upload_file(
                f'{INPUTS}/{document}',
                BUCKET,
                document
            )

    def _compare(
        self,
        document: str,
        old_type: str,
        new_type: str,
    ) -> None:
        """
        Converts `document` from `old_type` to `new_type` and then compares 
        the output with the expected output

        The path to the document being converted should be 
        s3://`BUCKET`.`document`.`old_type`

        The path to the expected output should be
        file://`EXPECTED`/`document`-`new_type`.txt

        :raise AssertionError: if the conversion output and the expected 
        output differ
        """
        if new_type == 'docx':
            read_function = self._read_docx
        elif new_type == 'pdf':
            read_function = self._read_pdf
        elif new_type == 'txt':
            read_function = self._read_txt
        else:
            raise ValueError(f'No read function exists for type "{new_type}"')

        self._invoke({
            'input_bucket': BUCKET,
            'input_path': f'{document}.{old_type}',
            'output_bucket': BUCKET,
            'output_path': f'{document}.{new_type}',
        })
        with TemporaryDirectory() as temp_dir:
            self.s3_client.download_file(
                BUCKET,
                f'{document}.{new_type}',
                f'{temp_dir}/{document}.{new_type}'
            )
            output = read_function(f'{temp_dir}/{document}.{new_type}')
            expected = self._read_txt(f'{EXPECTED}/{document}-{new_type}.txt')
            self.assertEqual(output, expected)

    def _invoke(self, event: dict[str, str]) -> dict[str, str]:
        """
        Invoke Unofunction with payload `event` and return the response 
        payload
        """
        response = self.lambda_client.invoke(
            FunctionName=FUNCTION,
            Payload=json.dumps(event).encode('utf-8')
        )
        payload = json.loads(response['Payload'].read().decode('utf-8'))

        if payload and 'errorMessage' in payload:
            raise Exception(payload)

        return payload

    def _read_docx(self, path: Path) -> str:
        """Reads DOCX"""
        document = Document(path)
        paragraphs = document.paragraphs

        return '\n'.join(paragraph.text for paragraph in paragraphs)

    def _read_pdf(self, path: Path) -> str:
        """
        Reads a PDF using OCR. This is to ensure fonts correctly rendered
        """
        pdf_image = pdf2image.convert_from_path(path)
        pdf_text = [
            pytesseract.image_to_string(page)
            for page in pdf_image
        ]

        return ''.join(pdf_text)

    def _read_txt(self, path: Path) -> str:
        """Reads TXT"""
        with open(path, 'r') as f:
            text = f.read()

        return text

    def test_docx_to_pdf(self) -> None:
        """Test DOCX to PDF conversion"""
        for document in [
            'churchill',
        ]:
            self._compare(document, 'docx', 'pdf')

    def test_docx_to_txt(self) -> None:
        """Test DOCX to TXT conversion"""
        for document in [
            'churchill',
        ]:
            self._compare(document, 'docx', 'txt')

    def test_txt_to_docx(self) -> None:
        """Test TXT to DOCX conversion"""
        for document in [
            'lincoln',
        ]:
            self._compare(document, 'txt', 'docx')

    def test_txt_to_pdf(self) -> None:
        """Test TXT to PDF conversion"""
        for document in [
            'lincoln',
        ]:
            self._compare(document, 'txt', 'pdf')
