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

class NotionBookClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    def parse_book_page(self, notion_book_page):
        page_id = notion_book_page["id"]
        book_title = notion_book_page["properties"]["Title"]["title"][0]["text"]["content"]
        author_name = notion_book_page["properties"]["Author"]["rich_text"][0]["text"]["content"]
        read_time = notion_book_page["properties"]["Read Seconds"]["number"]
        status = notion_book_page["properties"]["Status"]["status"]["name"]
        return {
            "page_id": page_id,
            "book_title": book_title,
            "author_name": author_name,
            "read_time": read_time,
            "status": status
        }

    # https://developers.notion.com/reference/post-database-query
    def get_book(self, book_title, author_name=None):
        if author_name is None:
            book_page = self.notion.databases.query(
                **{
                    "database_id": self.database_id,
                    "filter": {
                        "property": "Title",
                        "title": {
                            "equals": book_title,
                        },
                    },
                }
            )
            if len(book_page["results"]) != 0:
                return self.parse_book_page(book_page["results"][0])
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
                                    "equals": book_title,
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
                return self.parse_book_page(book_page["results"][0])
            else:
                return None

    # https://developers.notion.com/reference/patch-page
    def update_book(self, page_id, book):
        try:
            read_date = {"start": book.start_read_time.strftime("%Y-%m-%d"), "end": book.last_read_time.strftime("%Y-%m-%d")}

            progress = round(book.read_pages / book.total_pages, 2)
            # If progress > 90% and last read time over 48 hours, this book is treated as comleted
            if progress > 0.90 and datetime.datetime.now() - book.start_read_time > datetime.timedelta(hours=48):
                progress = 1.00
                status = "Completed"

            book_page = self.notion.pages.update(
                **{
                    "page_id": page_id,
                    "properties": {
                        "Read Seconds": {"number": book.read_time},
                        "Read Date": {"date": read_date},
                        "Progress": {"number": round(book.read_pages / book.total_pages, 2)},
                        "Status": {"status": {"name": status}}
                    },
                }
            )
            print(book.book_title, "successfully updated in notion")
            return self.parse_book_page(book_page)
        except KeyError as e:
            print("Error when updating", book.book_title, "by", book.author_name, "in notion")
            print(e)
            return None

    # https://developers.notion.com/reference/update-a-database
    def add_book(self, book):
        try:
            title = [{"text": {"content": book.book_title}}]
            author = [{"text": {"content": book.author_name}}]
            read_date = {"start": book.start_read_time.strftime("%Y-%m-%d"), "end": book.last_read_time.strftime("%Y-%m-%d")}

            status = "Reading" # Defaultly reading

            progress = round(book.read_pages / book.total_pages, 2)
            # If progress > 90% and last read time over 48 hours, this book is treated as comleted
            if progress > 0.90 and datetime.datetime.now() - book.start_read_time > datetime.timedelta(hours=48):
                progress = 1.00
                status = "Completed"

            book_page = self.notion.pages.create(
                **{
                    "parent": {
                        "database_id": self.database_id,
                    },
                    "properties": {
                        "Title": {"title": title},
                        "Author": {"rich_text": author},
                        "Read Seconds": {"number": book.read_time},
                        "Read Date": {"date": read_date},
                        "Progress": {"number": progress},
                        "Status": {"status": {"name": status}},
                    },
                }
            )
            print(book.book_title, "by", book.author_name, "successfully added to notion")
            return self.parse_book_page(book_page)
        except KeyError as e:
            print("Error when adding book to notion:", book.book_title, "by", book.author_name)
            print(e)
            return None