import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os

API_KEY = os.environ["NOTION_TOKEN"]
DATABASE_ID = "36c28ecfc10a46df9121466ec27874eb"

if __name__ == "__main__":
    # notion integration secret token
    token = os.environ["NOTION_TOKEN"]
    #  database id
    database_id = DATABASE_ID
    notion = notion_client.Client(auth=token)
    my_page = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "Name",
                "title": {
                    "contains": "科幻",
                },
            },
        }
    )
    for block in iterate_paginated_api(notion.databases.query, database_id=DATABASE_ID):
        print(block)