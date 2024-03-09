import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os
import logging
import re

class NotionDatabaseClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    def parse_book_page(self, notion_book_page):
        page_id = notion_book_page["results"][0]["id"]
        book_title = notion_book_page["results"][0]["properties"]["Title"]["title"][0]["text"]["content"]
        author_name = notion_book_page["results"][0]["properties"]["Author"]["rich_text"][0]["text"]["content"]
        read_time = notion_book_page["results"][0]["properties"]["Read Time"]["rich_text"][0]["text"]["content"]

        return {
            "page_id": page_id,
            "book_title": book_title,
            "author_name": author_name,
            "read_time": read_time
        }

    # https://developers.notion.com/reference/post-database-query
    def get_book(self, book_name, author_name=None):
        if author_name is None:
            book_page = self.notion.databases.query(
                **{
                    "database_id": self.database_id,
                    "filter": {
                        "property": "Title",
                        "title": {
                            "equals": book_name,
                        },
                    },
                }
            )
            if len(book_page["results"]) != 0:
                return self.parse_book_page(book_page)
            else:
                return None
        else:
            book_page = self.notion.databases.query(
                **{
                    "database_id": self.database_id,
                    "filter": {
                        "and": [
                            {
                                "property": "Title",
                                "title": {
                                    "equals": book_name,
                                },
                            },
                            {
                                "property": "Author",
                                "rich_text": {
                                    "equals": author_name,
                                },
                            },
                        ],
                    },
                }
            )

            if len(book_page["results"]) != 0:
                return self.parse_book_page(book_page)
            else:
                return None

    # https://developers.notion.com/reference/patch-page
    def update_book(self, page_id, book_name, author_name, read_time):
        try:
            read_time = [{"text": {"content": read_time}}]
            self.notion.pages.update(
                **{
                    "page_id": page_id,
                    "properties": {
                        "Read Time": {"rich_text": read_time},
                    },
                }
            )
            print(book_name, "successfully updated in notion")
        except KeyError as e:
            logging.error(e)
            print("Error when updating", book_name, "by", author_name, "in notion")

    # https://developers.notion.com/reference/update-a-database
    def add_book(self, book_name, author_name, read_time):
        try:
            titles = [{"text": {"content": book_name}}]
            authors = [{"text": {"content": author_name}}]
            read_time = [{"text": {"content": read_time}}]

            my_page = self.notion.pages.create(
                **{
                    "parent": {
                        "database_id": self.database_id,
                    },
                    "properties": {
                        "Title": {"title": titles},
                        "Author": {"rich_text": authors},
                        "Read Time": {"rich_text": read_time},
                    },
                }
            )
            print(book_name, "by", author_name, "successfully added to notion")
        except:
            print("Error when adding book to notion:", book_name, "by", author_name)