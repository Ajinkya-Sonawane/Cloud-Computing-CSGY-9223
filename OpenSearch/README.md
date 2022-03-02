### Create Domain (Elastic Search 7.10)
- Create domain 
- Provide Domain Name
- Deployment type - Development & Testing
- Version - Choose 7.10
- Data Nodes - Instance Type: `t3.small.search`
- Network - Public Access
- Fine-grained access policy: `Create master user`
- Access Policy: `Only use fine-grained access control`
- Create

### Create Domain (Open Search)
- Create domain 
- Provide Domain Name
- Deployment type - Development & Testing
- Version - Choose 1.1 (latest)
- Data Nodes - Instance Type: `t3.small.search`
- Network - Public Access
- Fine-grained access policy: `Set IAM ARN as master user`
- Access Policy: `Only use fine-grained access control`
- Add Following to resource policy :
`{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/<USER_NAME>"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:123456789012:domain/<DOMAIN_NAME>/*"
    }
  ]
}`

### Requirements (Open Search)
- `pip install requests`
- `pip install opensearch-py`
- `pip install requests_aws4auth`
- `pip install pyyaml`
- `pip install boto3`

### .ENV
- Store the domain name without the "https://" in OPEN_SEARCH_HOST key
- Store auth credentials required for requests
- Store the host domain url of Elastic Search
