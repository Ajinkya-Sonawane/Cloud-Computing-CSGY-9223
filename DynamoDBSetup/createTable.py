import boto3
import json

KEY_SCHEMA = json.load(open('KeySchema.json'))
ATTRIBUTE_DEFINITIONS = json.load(open('AttributeSchema.json'))
PROVISIONED_THROUGHPUT = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
TABLE_NAME = "tbl_Restaurants"

dynamodb = boto3.client('dynamodb')

if TABLE_NAME in dynamodb.list_tables()['TableNames']:
    print("\n%s table already exists" % TABLE_NAME)
else:
    tbl_Restaurants = dynamodb.create_table(TableName=TABLE_NAME,
                                            AttributeDefinitions = ATTRIBUTE_DEFINITIONS,
                                            KeySchema=KEY_SCHEMA,
                                            ProvisionedThroughput=PROVISIONED_THROUGHPUT)
    print("\n%s table created successfully" % TABLE_NAME)
