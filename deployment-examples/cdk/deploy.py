"""
Deploys Unofunction and creates an S3 bucket that Unofunction can read from
and write to

To install the AWS CDK, see 
https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html

To deploy this stack, run
    cdk deploy

To tear down this stack, run
    cdk destroy
Note that this will fail if the S3 bucket is not first emptied
"""
from aws_cdk import core as cdk
from aws_cdk import aws_lambda
from aws_cdk import aws_s3 as s3


class Unofunction(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda
        self.convert = aws_lambda.DockerImageFunction(
            code=aws_lambda.DockerImageCode.from_image_asset(
                cmd=['handler.handler'],
                directory='../../unofunction',
            ),
            id='unofunction',
            function_name='unofunction',

            # Must be at least 256 (megabytes). Larger instances run on faster
            # processors and hence convert files quicker
            memory_size=1024,

            scope=self,

            # It might be necessary to increase this for large files or batch
            # conversion
            timeout=cdk.Duration.seconds(300),
        )

        # S3
        self.storage = s3.Bucket(
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,

            # Uncomment the line below to set the bucket name. Note that
            # bucket names must be unique across AWS' global namespace
            # bucket_name='BUCKET_NAME',

            encryption=s3.BucketEncryption.S3_MANAGED,
            id='storage',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            scope=self,
        )
        self.storage.grant_read_write(self.convert)


app = cdk.App()
lambdas = Unofunction(scope=app, construct_id='Unofunction')
app.synth()
