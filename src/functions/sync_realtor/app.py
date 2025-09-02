import json
import os
from common.db import get_table
from common.http import http_get
from common.serialization import to_jsonable


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_jsonable),
    }


def handler(event, context):
    table = get_table(os.environ["TABLE_NAME"]) 

    # Placeholder logic: call Realtor (mocked) and upsert items
    # Replace with real endpoint + auth
    sample_listings = [
        {"id": "re-1", "source": "realtor", "price": 500000, "city": "Austin"},
        {"id": "re-2", "source": "realtor", "price": 750000, "city": "Denver"},
    ]

    with table.batch_writer() as batch:
        for item in sample_listings:
            batch.put_item(Item=item)

    return _response(200, {"message": "Realtor sync complete", "count": len(sample_listings)})
