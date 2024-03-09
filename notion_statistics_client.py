import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os
import logging
import re

class NotionStatisticsClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)

    # https://developers.notion.com/reference/post-database-query
    def get_total_statistics(self):
        page = self.notion.databases.query(
            **{
                "database_id": self.database_id,
                "filter": {
                    "property": "Time Range",
                    "title": {
                        "equals": "Total",
                    },
                },
            }
        )
        return page["results"][0]["id"]

    # Updating total by adding all books in the notion book dataset into relation
    def update_total(self, nob):
        total_page_id = self.get_total_statistics()

        # titles = [{"text": {"content": "Test"}}]
        # relation = [{"id": nob.database_id, "relation": {"database_id": nob.database_id, "synced_property_name": "血清素",}}]

        # my_page = self.notion.pages.create(
        #     **{
        #         "parent": {
        #             "database_id": self.database_id,
        #         },
        #         "properties": {
        #             "Time Range": {"title": titles},
        #             "Book Relation": {"relation": relation},
        #         },
        #     }
        # )
        # print(my_page)
        relations = []
        for block in iterate_paginated_api(nob.notion.databases.query, database_id=nob.database_id):
            relations.append({"id": block["id"], "relation": {"database_id": nob.database_id}})

        page = self.notion.pages.update(
            **{
                "page_id": total_page_id,
                "properties": {
                    "Book Relation": {
                        "relation": relations
                    },
                },
            }
        )
        print(page)