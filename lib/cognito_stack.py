from constructs import Construct
from aws_cdk import Stack
from aws_cdk import aws_cognito as cognito
from aws_cdk import Stack, CfnOutput


class CognitoStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a new Cognito User Pool
        self.user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name="MyUserPool",
            self_sign_up_enabled=True,  # allow users to sign up
            auto_verify=cognito.AutoVerifiedAttrs(  # auto verify email and phone number
                email=True, phone=False
            ),
        )

        # Create a Cognito User Pool Client
        self.user_pool_client = cognito.UserPoolClient(
            self,
            "UserPoolClient",
            user_pool=self.user_pool,
            generate_secret=True,  # generate client secret
        )

        # Output the User Pool and Client id's
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            export_name="UserPoolId",
        )
        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            export_name="UserPoolClientId",
        )
