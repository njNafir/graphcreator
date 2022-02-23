# Overview

Build a chatbot that returns the shortest distance between two cities/nodes in a directed
graph, where all edges weigh 1. 

    Step 1 AWS Graph Creator Lambda Function
    Step 2 AWS Lex
    Step 3 Lex with Lambda
    Step 4 Identity Pool and Lex Configuration
    Step 5 Static Website to Test Chatbot


## Links

The hosted static website is there:

    http://graphcreator.s3-website-us-east-1.amazonaws.com/


## Resources

### S3

    Bucket name: graphcreator
    Bucket Policy: 
        
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": "arn:aws:s3:::graphcreator/*"
                }
            ]
        }


### IAM

    Cognito_graphcreatorAuth_Role
    
        AmazonPollyReadOnlyAccess
        AmazonLexRunBotsOnly

    Cognito_graphcreatorUnauth_Role
    
        AmazonPollyReadOnlyAccess
        AmazonLexRunBotsOnly

    lambda-dynamodb-access

        Full Access to: Dynamodb, APIGateway, Lex, Cloudwatch


### Dynamodb

    Table:

        city-distance
    
    Fields

        source, destination, distance


### IdentityPool

    Credentials

        // Initialize the Amazon Cognito credentials provider
        AWS.config.region = 'us-east-1'; // Region
        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
            IdentityPoolId: 'us-east-1:bf45dbf1-91ab-49ff-aeb0-fc2a04a33dd8',
        });


### API Gateway

    URL: https://yk4584pwy6.execute-api.us-east-1.amazonaws.com/default/get-distance
    Method: POST
    API-Key: h2prn37Vzl9IcPAEMqJhA1NytJpyoGtaKripWyE8
    Request Body: {
        "currentIntent": {
            "name": "FindBitcoinPrice",
            "slots": {
            "Source": "Chicago",
            "Destination": "Urbana"
            }
        }
    }

    URL: https://yk4584pwy6.execute-api.us-east-1.amazonaws.com/default/store-distance
    Method: POST
    API-Key: h2prn37Vzl9IcPAEMqJhA1NytJpyoGtaKripWyE8
    Request Body: {
        "graph": "Chicago->Urbana,Urbana->Springfield,Chicago->Lafayette"
    }


### Lex

    Botname: getDistance
    Fullfillment: get-distance (lambda function)

    Intent: getCityDistance
    Variable: Source, Destination (Not required)

    Intent: getCityDistancePopUp
    Variable: Source, Destination (Required)
