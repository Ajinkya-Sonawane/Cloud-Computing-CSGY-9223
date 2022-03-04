from decouple import config
import yaml
import json
import requests


PATH = "../YelpDataFetcher/"
CUISINES_LIST = ['Indian', 'Mexican', 'Chinese', 'Korean', 'Japanese']
AUTH_CREDS = (config("AUTH_USERNAME"),config("AUTH_PWD"))
HOST_URL = config("HOST_URL")
index_name = config("ES_INDEX_NAME")
type_name = config("INDEX_TYPE")
region = config("REGION")
service = config("SERVICE")


def create_index(index_name):
    url = '%s/%s' % (HOST_URL, index_name)
    response = requests.put(url, auth=AUTH_CREDS)
    print (response.json())


def create_type(index_name, type_name):
    url = '%s/%s/%s/_mapping' % (HOST_URL, index_name, type_name)
    headers = {"Content-Type": "application/json"}
    body = {
        "restaurant": {
            "properties": {
                "restaurant_id": {
                    "type": "text"
                },
                "cuisine": {
                    "type": "text"
                }
            }
        }
    }
    params = {
        "include_type_name": "true"
    }
    response = requests.put(url, auth=AUTH_CREDS, data=json.dumps(body), params=params, headers=headers)
    print (response.json())


def upload_json_to_index(index_name):
    url = '%s/%s/_doc/' % (HOST_URL, index_name)
    for filename in CUISINES_LIST:
        data = yaml.safe_load(open("%s%s.json" % (PATH, filename)))
        for record in data:
            document = {"restaurant_id": record["id"], "cuisine": filename}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, auth=AUTH_CREDS, data=json.dumps(document), headers=headers)
            print(response.json())


def delete_index(index_name):
    url = '%s/%s' % (HOST_URL, index_name)
    response = requests.delete(url, auth=AUTH_CREDS)
    print (response.json())


def search_data_on_index(index_name, cuisine):
    # Search for the document.
    query = {
        'query': {
            'multi_match': {
                'query': cuisine,
                'fields': ['cuisine']
            }
        }
    }
    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = {"Content-Type": "application/json"}

    url = "%s/%s/_search" % (HOST_URL, index_name)

    # Make the signed HTTP request
    response = requests.get(url, auth=AUTH_CREDS, headers=headers, data=json.dumps(query)).json()
    print('\nSearch results:')
    for record in response['hits']['hits']:
        print(record)


if __name__ == "__main__":
    create_index(index_name)
    create_type(index_name,type_name)
    upload_json_to_index(index_name)
    search_data_on_index(index_name,"Indian")
    #---------WARNING----------
    #delete_index('restaurants')
