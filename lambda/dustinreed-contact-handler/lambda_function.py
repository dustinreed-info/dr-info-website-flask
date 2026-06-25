import json
import os

import boto3

ses = boto3.client("ses")

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@dustinreed.info")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "dustin@dustinreed.info")
SITE_NAME = os.environ.get("SITE_NAME", "Dustin Reed Website")


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        body = json.loads(event.get("body", "{}"))
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    name = body.get("name", "N/A")
    email = body.get("email")
    subject_input = body.get("subject", "Contact form submission")
    message = body.get("message")

    if not email or not message:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Email and message are required"}),
        }

    email_subject = f"New Contact Form: {subject_input}"
    email_body = f"""New message from {SITE_NAME}:

Name: {name}
From: {email}
Subject: {subject_input}

Message:
{message}
"""

    try:
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [RECIPIENT_EMAIL]},
            ReplyToAddresses=[email],
            Message={
                "Subject": {"Data": email_subject},
                "Body": {"Text": {"Data": email_body}},
            },
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully"}),
        }
    except Exception as e:
        print(f"SES Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to send email"}),
        }
