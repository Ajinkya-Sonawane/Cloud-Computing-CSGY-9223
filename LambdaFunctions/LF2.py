import json
import boto3
import requests
import smtplib
import os

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
ES_HOST_URL = os.environ['ES_HOST_URL']
ES_INDEX_NAME = os.environ['ES_INDEX_NAME']
ES_AUTH = (os.environ['ES_USER_NAME'], os.environ['ES_USER_PWD'])
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_APP_PWD = os.environ['GMAIL_APP_PWD']
SENT_FROM = GMAIL_USER


def fetch_message_from_sqs():
    # Create SQS client
    sqs = boto3.client('sqs')

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=1,
    )
    if response.get('Messages'):
        message = response['Messages'][0]
        message_body = json.loads(message['Body'])
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
        return {"msgtype": 200, "body": message_body}
    else:
        return {"msgtype": 404, "body": {}}


def fetch_restaurant_id_from_es(cuisine):
    url = '%s/%s/_search' % (ES_HOST_URL, ES_INDEX_NAME)
    query = {
        'size': 5,
        'query': {
            'multi_match': {
                'query': cuisine,
                'fields': ['cuisine']
            }
        }
    }

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = {"Content-Type": "application/json"}

    # Make the signed HTTP request
    response = requests.get(url, auth=ES_AUTH, headers=headers, data=json.dumps(query)).json()

    # Add the search results to the response
    records = response['hits']['hits']
    return records


def fetch_restaurant_details_from_dynamodb(restaurant_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={'restaurant_id': restaurant_id})
    return response


def create_content(restaurant_details, message):
    contents = {
        'email': message["body"]["email"],
        'cuisine': message["body"]["cuisine"],
        'location': message["body"]["location"],
        'count': message["body"]["count"],
        'day': message["body"]["day"],
        'time': message["body"]["time"],
        'restaurants': list()
    }
    for restaurant in restaurant_details:
        content = {
            'name': restaurant['Item']['name'],
            'address': restaurant['Item']['address'],
            'contact': restaurant['Item']['contact'],
            'latitude': restaurant['Item']['coordinates']['latitude'],
            'longitude': restaurant['Item']['coordinates']['longitude'],
        }
        contents['restaurants'].append(content)
    return contents


def send_email(contents):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(GMAIL_USER, GMAIL_APP_PWD)
        maps_url = "https://maps.google.com/?q="
        sent_subject = "Chatbot Restaurant Suggestions"
        sent_body = """Here are a few suggestion for %s cuisine in %s\nNumber of people: %s on %s at %s :\n""" % \
                    (contents["cuisine"], contents["location"], contents['count'], contents['day'], contents['time'])
        for content in contents['restaurants']:
            sent_body += "\n\n%s\nAddress: %s\nContact:%s\nLocation: %s%s,%s" % (content["name"],
                                                                                 ' '.join(content["address"]),
                                                                                 content["contact"], maps_url,
                                                                                 content["latitude"],
                                                                                 content["longitude"])

        SENT_TO = contents["email"]
        msg = "Subject:%s\n\n%s" % (sent_subject, sent_body)
        print('Sending email now!!!')
        server.sendmail(SENT_FROM, SENT_TO, msg)
        server.quit()
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


def lambda_handler(event, context):
    message = fetch_message_from_sqs()
    if message['msgtype'] == 200:
        records = fetch_restaurant_id_from_es(message['body']['cuisine'])
        restaurant_details = []
        for record in records:
            restaurant_details.append(fetch_restaurant_details_from_dynamodb(record["_source"]["restaurant_id"]))
        contents = create_content(restaurant_details, message)
        send_email(contents)
    else:
        message = {'message': "Not Found"}
    return {
        'statusCode': 200,
        'body': message
    }
