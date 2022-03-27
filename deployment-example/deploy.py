from aws_cdk import core as cdk
from aws_cdk import aws_lambda
from aws_cdk import aws_s3 as s3


class Unofunction(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambdas
        self.convert = aws_lambda.DockerImageFunction(
            code=aws_lambda.DockerImageCode.from_image_asset(
                cmd=['handler.handler'],
                directory='../unofunction',
            ),
            id='unofunction',
            function_name='unofunction',

            # Larger instances run on faster processes
            memory_size=1024,

            scope=self,

            # It might be necessary to increase this for large files or batch
            # conversion
            timeout=cdk.Duration.seconds(300),
        )

        # Storage
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
