import json
import boto3
import os

client = boto3.client('polly')
bucket_name = os.getenv("BUCKET_NAME")
region = os.getenv("REGION")


def get_status(task_id):
    response = client.get_speech_synthesis_task(
        TaskId=task_id
    )
    return response['SynthesisTask']['TaskStatus']


def start_job(text):
    response = client.start_speech_synthesis_task(
        Engine='standard',
        LanguageCode='en-IN',
        OutputFormat='mp3',
        OutputS3BucketName=bucket_name,
        Text=text,
        TextType='text',
        VoiceId='Aditi')
    task_id = response['SynthesisTask']['TaskId']
    while get_status(task_id) != 'completed' or get_status(task_id) != 'failed':
        pass
    status = get_status(task_id)
    if status == 'completed':
        return task_id
    else:
        return None


def download_file(task_id):
    s3_client = boto3.client('s3', region)
    res = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket_name,
                                                   'Key': "{}.mp3".format(task_id)},
                                           ExpiresIn=180)
    return res


def handler(event, context):
    print(event)
    text = event['query']['text']
    task_id = start_job(text)
    if task_id:
        link = download_file(task_id)
        print_link = '<a href="'+link+'">link text</a>'
        return {
            'statusCode': 200,
            'Download Your Mp3': json.dump(print_link)
        }
    else:
        return {
            'statusCode': 200,
            'Body': json.dumps('failed')
        }
