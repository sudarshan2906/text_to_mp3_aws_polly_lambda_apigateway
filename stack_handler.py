import boto3
from botocore.client import ClientError


class Stack:
    def __init__(self, stack_name, template_url, region, parameters=None):
        self.stack_name = stack_name
        self.template_url = template_url
        self.client_cloudformation = boto3.client('cloudformation', region_name=region)
        self.client_s3 = boto3.client('s3', region_name=region)
        self.parameters = parameters
        self.waiter_config = {
                                'Delay': 5,
                                'MaxAttempts': 120
                            }
        self.update_stack()

    def create_stack(self):
        try:
            self.client_cloudformation.create_stack(
                StackName=self.stack_name,
                TemplateURL=self.template_url,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=self.parameters
            )
            waiter = self.client_cloudformation.get_waiter('stack_create_complete')
            print("Creating stack : {}".format(self.stack_name))
            waiter.wait(StackName=self.stack_name, WaiterConfig=self.waiter_config)
        except ClientError as ce:
            print(ce)

    def update_stack(self):
        try:
            self.client_cloudformation.update_stack(
                StackName=self.stack_name,
                TemplateURL=self.template_url,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=self.parameters
            )
            waiter = self.client_cloudformation.get_waiter('stack_update_complete')
            print("Updating stack : {}".format(self.stack_name))
            waiter.wait(StackName=self.stack_name, WaiterConfig=self.waiter_config)
        except ClientError as ce:
            if "does not exist" in ce.response['Error']['Message']:
                self.create_stack()
            else:
                print(ce)