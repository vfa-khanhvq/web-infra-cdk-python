from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    RemovalPolicy,
    aws_iam as iam,
)
from constructs import Construct
class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = vpc
    
    def create_s3_bucket(self, name):
        return  s3.Bucket(self,
                "Bucket " + name,
                removal_policy=RemovalPolicy.DESTROY,  # NOT recommended for production code
                auto_delete_objects=True)

    def create_s3_static_host(self, name):
        # Create an S3 bucket
        bucket = self.create_s3_bucket(self, name)

        # Create an Origin Access Identity (OAI)
        oai = cloudfront.OriginAccessIdentity(self, "OAI " + name)

        # Grant read access to CloudFront OAI
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.CanonicalUserPrincipal(oai.cloudfront_origin_access_identity_s3_canonical_user_id)]
        ))

        # Create a CloudFront distribution
        distribution = cloudfront.Distribution(self, "Distribution " + name,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object="index.html"
        )
        return distribution