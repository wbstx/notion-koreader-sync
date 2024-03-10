import requests
import json
import notion_client
from notion_client.helpers import iterate_paginated_api
import os
import logging
import re

class NotionBookClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    def parse_book_page(self, notion_book_page):
        page_id = notion_book_page["results"][0]["id"]
        book_title = notion_book_page["results"][0]["properties"]["Title"]["title"][0]["text"]["content"]
        author_name = notion_book_page["results"][0]["properties"]["Author"]["rich_text"][0]["text"]["content"]
        read_time = notion_book_page["results"][0]["properties"]["Read Seconds"]["number"]
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
    def update_book(self, page_id, book):
        try:
            read_date = {"start": book.start_read_time.strftime("%Y-%m-%d"), "end": book.last_read_time.strftime("%Y-%m-%d")}
            self.notion.pages.update(
                **{
                    "page_id": page_id,
                    "properties": {
                        "Read Seconds": {"number": book.read_time},
                        "Read Date": {"date": read_date},
                        "Progress": {"number": round(book.read_pages / book.total_pages, 2)}
                    },
                }
            )
            print(book.book_name, "successfully updated in notion")
        except KeyError as e:
            logging.error(e)
            print("Error when updating", book.book_name, "by", book.author_name, "in notion")

    # https://developers.notion.com/reference/update-a-database
    def add_book(self, book):
        try:
            title = [{"text": {"content": book.book_name}}]
            author = [{"text": {"content": book.author_name}}]
            read_date = {"start": book.start_read_time.strftime("%Y-%m-%d"), "end": book.last_read_time.strftime("%Y-%m-%d")}

            my_page = self.notion.pages.create(
                **{
                    "parent": {
                        "database_id": self.database_id,
                    },
                    "properties": {
                        "Title": {"title": title},
                        "Author": {"rich_text": author},
                        "Read Seconds": {"number": book.read_time},
                        "Read Date": {"date": read_date},
                        "Progress": {"number": round(book.read_pages / book.total_pages, 2)}
                    },
                }
            )
            print(book.book_name, "by", book.author_name, "successfully added to notion")
        except KeyError as e:
            print("Error when adding book to notion:", book.book_name, "by", book.author_name)
            print(e)