import boto3
import config
from botocore.client import ClientError
import functions
import stack_handler as stack
import api_gateway as api
import index


def upload_html(bucket_name, file_name):
    data = open(file_name, 'rb')
    s3_resource = boto3.resource('s3', region_name=config.REGION)
    s3_resource.Bucket(bucket_name).put_object(Key=file_name, Body=data, ContentType='text/html')


def upload_template_python_scripts():
    s3_client = boto3.client('s3', region_name=config.REGION)
    try:
        s3_client.create_bucket(Bucket=config.MAIN_BUCKET,
                                CreateBucketConfiguration={'LocationConstraint': config.REGION})
    except ClientError as ce:
        if ce.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print("Data Bucket Already Created")
        else:
            print(ce)
    s3_client.put_bucket_versioning(Bucket=config.MAIN_BUCKET, VersioningConfiguration={'Status': 'Enabled'})
    functions_obj = functions.Functions(config.REGION)
    functions_obj.upload_file_folder(config.MAIN_BUCKET, "template")
    functions_obj.upload_zip_object(config.MAIN_BUCKET, "lambda_function.py", "lambda_function.zip",
                                    "lambda_function.zip")
    config.LAMBDA_VERSION = functions_obj.get_version_opject(config.MAIN_BUCKET, "lambda_function.zip")


def get_parameters(params):
    new_params = []
    for key in params:
        new_params.append({'ParameterKey': key, 'ParameterValue': params[key]})
    return new_params


if __name__ == "__main__":
    upload_template_python_scripts()

    # stack create and update

    parameters = {"MainBucket": config.MAIN_BUCKET,
                  "HostBucketName": config.HOST_BUCKET_NAME,
                  "Region": config.REGION,
                  "LambdaVersion": config.LAMBDA_VERSION}
    stack_obj = stack.Stack(config.STACK_NAME, config.TEMPLATE_URL, config.REGION, get_parameters(parameters))

    # deploying the api gateway

    api_gateway = api.Api(config.API_NAME, config.REGION)
    api_id = api_gateway.get_api_id()
    api_gateway.create_deployment()
    api_url = api_id + ".execute-api.ap-south-1.amazonaws.com/test"
    print("Api Deployed : {}".format(api_url))

    # adding api_url to index.html and uploading it

    index.create_html(api_url)
    upload_html(config.HOST_BUCKET_NAME, "index.html")
    print("http://{}.s3-website.{}.amazonaws.com".format(config.HOST_BUCKET_NAME, config.REGION))
