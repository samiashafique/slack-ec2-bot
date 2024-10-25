import boto3
import os
import requests
from dotenv import load_dotenv

#Load environment variables
load_dotenv()
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

#AWS EC2 Client
ec2 = boto3.client('ec2')

def list_untagged_instances():
    response = ec2.describe_instances (
        Filters = [
            {
                'Name' : 'tag-key',
                'Values' : []
            }
        ]
    )

    untagged_instances = []
    for reservation in response ['Reservations'] :
        for instance in reservation ['Instances'] :
            if 'Tags' not in instance:
                untagged_instances.append(instance['InstanceId'])
    return untagged_instances
def stop_instances(instance_ids):
    ec2.stop_instances(InstanceIds=instance_ids)
def send_slack_message(text):
    payload = {'text': text}
    response = requests.post(slack_webhook_url, json=payload)
    return response.status_code

if __name__ == "__main__":
    untagged_instances = list_untagged_instances()
    if untagged_instances:
        stop_instances(untagged_instances)
        message = f"Stopped untagged instances: {', '.join(untagged_instances)}"
    else:
        message = "No untagged instances found."
    send_slack_message(message)


