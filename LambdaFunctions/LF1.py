import json
import boto3
import re
import os
import datetime
import time

sqs = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']
os.environ['TZ'] = 'America/New_York'
time.tzset()


def validate_values(slots, slotName, slotValue):
    response = {"status": 200, "message": ""}
    if slotName == "location":
        if slotValue.lower() not in ['new york', 'nyc', 'new york city', 'brooklyn', 'manhattan', 'bronx',
                                     'staten island', 'queens']:
            response = {"status": 400, "message": "Sorry, we only serve in New York City"}
    elif slotName == "day":
        if datetime.datetime.strptime(slotValue, '%Y-%m-%d').date() < datetime.datetime.now().date():
            response = {"status": 400, "message": "Kindly provide day/date in future"}
    elif slotName == "time":
        if datetime.datetime.strptime("%s %s" % (slots['day'], slotValue), '%Y-%m-%d %H:%M') < datetime.datetime.now():
            response = {"status": 400, "message": "Kindly provide a time in future"}
    elif slotName == "count":
        if int(slotValue) not in range(1, 21):
            response = {"status": 400, "message": "Number of people should be between 1 and 20"}
    elif slotName == "cuisine":
        if slotValue.lower() not in ['indian', 'mexican', 'chinese', 'japanese', 'korean']:
            response = {"status": 400,
                        "message": "Sorry, available cuisines are Indian, Mexican, Chinese, Japanese and Korean"}
    elif slotName == "email":
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(regex, slotValue):
            response = {"status": 400, "message": "Kindly provide a valid email address"}
    return response


def extract_slots(slots):
    slotToElicit = None
    slot_names = ['location', 'cuisine', 'day', 'time', 'count', 'email']
    for slot_name in slot_names:
        if not slots.get(slot_name):
            slotToElicit = slot_name
            return {"status": 404, "slotToElicit": slot_name, "message": ""}
        response = validate_values(slots, slot_name, slots[slot_name])
        if response['status'] != 200:
            return {"status": 400, "slotToElicit": slot_name, "message": response["message"]}
    return {"status": 200, "slotToElicit": slotToElicit, "message": ""}


def send_message_to_SQS(slots):
    msg = {
        'location': slots['location'],
        'cuisine': slots['cuisine'],
        'day': slots['day'],
        'time': slots['time'],
        'count': slots['count'],
        'email': slots['email']
    }

    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageBody=json.dumps(msg),
        MessageGroupId='LF1'
    )


def lambda_handler(event, context):
    type = "ElicitSlot"
    result = extract_slots(event['currentIntent']['slots'])
    response = {
        "dialogAction": {}
    }
    if result["status"] != 200:
        response['dialogAction']['type'] = 'ElicitSlot'
        response['dialogAction']['intentName'] = 'DiningSuggestionsIntent'
        response['dialogAction']['slots'] = event['currentIntent']['slots']
        response['dialogAction']['slotToElicit'] = result["slotToElicit"]
        if result["status"] == 400:
            response['dialogAction']['message'] = dict()
            response['dialogAction']['message']['contentType'] = 'PlainText'
            response['dialogAction']['message']['content'] = result["message"]
    else:
        send_message_to_SQS(event['currentIntent']['slots'])
        response['dialogAction']['type'] = 'Close'
        response['dialogAction']['fulfillmentState'] = 'Fulfilled'
        response['dialogAction']['message'] = dict()
        response['dialogAction']['message']['contentType'] = 'PlainText'
        response['dialogAction']['message']['content'] = 'Great, restaurant suggestions will be emailed to you shortly'
    return response