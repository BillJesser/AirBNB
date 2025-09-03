import json
import os
import boto3


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event, context):
    table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"]) 

    # Placeholder logic: simulate Zillow ingestion
    sample_listings = [
        {"id": "zi-1", "source": "zillow", "price": 600000, "city": "Seattle"},
        {"id": "zi-2", "source": "zillow", "price": 820000, "city": "Miami"},
    ]

    with table.batch_writer() as batch:
        for item in sample_listings:
            batch.put_item(Item=item)

    return _response(200, {"message": "Zillow sync complete", "count": len(sample_listings)})
