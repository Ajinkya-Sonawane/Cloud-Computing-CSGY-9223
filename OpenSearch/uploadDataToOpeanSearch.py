from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from decouple import config
import boto3
import yaml


PATH = "../YelpDataFetcher/"
CUISINES_LIST = ['Indian', 'Mexican', 'Chinese', 'Korean', 'Japanese']
index_name = config("OS_INDEX_NAME")
region = config("REGION")
service = config("SERVICE")
creds = boto3.Session().get_credentials()
awsauth = AWS4Auth(creds.access_key, creds.secret_key, region, service, session_token=creds.token)
host = config("OPEN_SEARCH_HOST")
client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def create_index():
    index_body = {
        'settings': {
            'index': {
            }
        }
    }
    response = client.indices.create(index_name, body=index_body)


def upload_json_to_index():
    records = []
    id = 1
    for filename in CUISINES_LIST:
        data = yaml.safe_load(open("%s%s.json" % (PATH, filename)))
        for record in data:
            document = {"restaurant_id": record["id"], "cuisine": filename}
            response = client.index(
                index='restaurant-index',
                body=document,
                id=id,
                refresh=True
            )
            id += 1
            print(response)


def search_data_on_index():
    # Search for the document.
    q = 'Indian'
    query = {
        'size': 5,
        'query': {
            'multi_match': {
                'query': q,
                'fields': ['cuisine']
            }
        }
    }

    response = client.search(
        body=query,
        index=index_name
    )
    print('\nSearch results:')
    for record in response['hits']['hits']:
        print(record)


if __name__ == "__main__":
    create_index()
    upload_json_to_index()
    search_data_on_index()
