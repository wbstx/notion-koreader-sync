import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os
import logging
import re
import datetime
from utils.bookinfo_format import author_name_format

# Notion API format cheatsheet
# https://developers.notion.com/reference/property-value-object#status-property-values

class NotionQuoteClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    def quote_format(self, quote, max_length=30):
        sentences = re.split(r'[\.\!\?\,\。\？\！\，]', quote.text)
        index = 0
        for sentence in sentences:
            sentence = sentence.strip()
            index += len(sentence) + 1
            if index > max_length:
                break
        return quote.text[:index-1] + "... —— " + author_name_format(quote.author_name) + " 《" + quote.book_title + "》"


    def is_quote_exists(self, quote):
        quote_page = self.notion.databases.query(
            **{
                "database_id": self.database_id,
                "filter": {
                    "property": "Create Timestamp",
                    "rich_text": {
                        "equals": str(int(quote.create_time.timestamp())),
                    },
                },
            }
        )
        if len(quote_page["results"]) != 0:
            return True
        else:
            return False

    # https://developers.notion.com/reference/update-a-database
    def add_quote(self, quote, nob, koreader_notion_map):
        if not self.is_quote_exists(quote):
            quote_text = [{"text": {"content": self.quote_format(quote)}}]
            chapter = [{"text": {"content": quote.chapter}}]
            create_timestamp = [{"text": {"content": str(int(quote.create_time.timestamp()))}}]
            book = [{"id": koreader_notion_map[quote.ko_id], "relation": {"database_id": nob.database_id}}]
            quote_content = [{"text": {"content": quote.text}}]

            quote_page = self.notion.pages.create(
                **{
                    "parent": {
                        "database_id": self.database_id,
                    },
                    "properties": {
                        "Quote": {"title": quote_text},
                        "Book": {"relation": book},
                        "Chapter": {"rich_text": chapter},
                        "Create Timestamp": {"rich_text": create_timestamp},
                        "Quote Content": {"rich_text": quote_content}
                    },
                }
            )

        # print(day_name, "successfully added to notion")