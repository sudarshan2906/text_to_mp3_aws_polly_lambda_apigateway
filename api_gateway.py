import boto3


class Api:
    def __init__(self, api_name, region):
        self.api_name = api_name
        self.api_id = ""
        self.client_api_gateway = boto3.client('apigateway', region_name=region)

    def get_api_id(self):
        response = self.client_api_gateway.get_rest_apis()
        for api in response['items']:
            if api['name'] == self.api_name:
                self.api_id = api['id']
        return self.api_id

    def create_deployment(self):
        response = self.client_api_gateway.create_deployment(restApiId=self.api_id, stageName='test')
