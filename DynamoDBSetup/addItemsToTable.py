import decimal

import boto3
import json
import time
import yaml

TABLE_NAME = "tbl_Restaurants"
CUISINES_LIST = ['Indian', 'Mexican', 'Chinese', 'Korean', 'Japanese']
PATH_TO_FILE = "../YelpDataFetcher/"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

for filename in CUISINES_LIST:
    filepath = "%s%s.json" % (PATH_TO_FILE, filename)
    data = yaml.safe_load(open(filepath))
    count = 1
    for record in data:
        ITEM = {
            "restaurant_id": str(record["id"]),
            "name": record["name"],
            "address": record["location"]["display_address"],
            "zipcode": str(record["location"]["zip_code"]),
            "coordinates": {"latitude": str(record["coordinates"]["latitude"]),
                            "longitude": str(record["coordinates"]["longitude"])},
            "contact": str(record["phone"]),
            "rating": str(record["rating"]),
            "review_count": str(record["review_count"]),
            "transactions": record["transactions"],
            "insertAtTimestamp": str(time.time())
        }
        table.put_item(TableName=TABLE_NAME, Item=ITEM)
        print("%d records added" % count)
        count += 1
    print("%s cuisine items added" % filename)
