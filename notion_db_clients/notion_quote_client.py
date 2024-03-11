import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os
import logging
import re
import datetime

# Notion API format cheatsheet
# https://developers.notion.com/reference/property-value-object#status-property-values

class NotionQuoteClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    # https://developers.notion.com/reference/update-a-database
    def add_quote(self, quote, nob, koreader_notion_map):
        quote_text = [{"text": {"content": quote.text}}]
        chapter = [{"text": {"content": quote.chapter}}]
        create_timestamp = [{"text": {"content": str(int(quote.create_time.timestamp()))}}]
        book = [{"id": koreader_notion_map[quote.ko_id], "relation": {"database_id": nob.database_id}}]

        quote_page = self.notion.pages.create(
            **{
                "parent": {
                    "database_id": self.database_id,
                },
                "properties": {
                    "Quote": {"title": quote_text},
                    "Book": {"relation": book},
                    "Chapter": {"rich_text": chapter},
                    "Create Timestamp": {"rich_text": create_timestamp}
                },
            }
        )

        # print(day_name, "successfully added to notion")