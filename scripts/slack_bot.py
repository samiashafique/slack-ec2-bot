import boto3
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Slack Webhook URL from the .env file
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

# AWS EC2 client
ec2 = boto3.client('ec2')

# Function to list untagged EC2 instances
def list_untagged_instances():
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']  # You can filter for running instances only
            }
        ]
    )
    untagged_instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Extract tags (if any)
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            # If the 'Name' tag is not found, it's considered untagged
            if 'Name' not in tags:
                untagged_instances.append(instance['InstanceId'])

    return untagged_instances

# Function to stop untagged instances
def stop_instances(instance_ids):
    ec2.stop_instances(InstanceIds=instance_ids)

# Function to send a message to Slack
def send_slack_message(text):
    payload = {'text': text}
    response = requests.post(slack_webhook_url, json=payload)
    return response.status_code

# Main function to run the bot
if __name__ == "__main__":
    untagged_instances = list_untagged_instances()
    if untagged_instances:
        # Stop untagged instances
        stop_instances(untagged_instances)
        # Prepare message with stopped instance IDs
        message = f"Stopped untagged instances: {', '.join(untagged_instances)}"
    else:
        # No untagged instances found
        message = "No untagged instances found."

    # Send the message to Slack
    send_slack_message(message)
