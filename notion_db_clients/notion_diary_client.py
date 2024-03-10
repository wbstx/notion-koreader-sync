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

class NotionDiaryClient:
    def __init__(self, database_id, API_KEY):
        self.database_id = database_id
        self.notion = notion_client.Client(auth=API_KEY)
    
    # https://developers.notion.com/reference/post-database-query
    def get_last_day(self):
        day_page = self.notion.databases.query(
            **{
                "database_id": self.database_id,
                "sorts": [{
                    "property": "Daydate",
                    "direction": "descending",
                }],
            }
        )
        return day_page["results"][0]["properties"]["Daydate"]["date"]["start"]
    
    def get_day(self, day):
        day_page = self.notion.databases.query(
            **{
                "database_id": self.database_id,
                "filter": {
                    "property": "Day",
                    "title": {
                        "equals": day,
                    },
                },
            }
        )

        if len(day_page["results"]) != 0:
            return day_page["results"][0]["id"]
        else:
            return None

    # https://developers.notion.com/reference/patch-page
    def update_day(self, page_id, day_stat, koreader_notion_map):
        read_time = day_stat.day_read_time
        try:
            day_page = self.notion.pages.update(
                **{
                    "page_id": page_id,
                    "properties": {
                        "Read Seconds": {"number": read_time},
                    },
                }
            )
            print(day_stat.day.strftime('%Y-%m-%d'), "successfully updated in notion")
            return day_page["id"]
        except KeyError as e:
            print("Error when updating", day_stat.day.strftime('%Y-%m-%d'), "in notion")
            print(e)
            return None

    # https://developers.notion.com/reference/update-a-database
    def add_day(self, day_stat, nob, koreader_notion_map):
        day_name = day_stat.day.strftime('%Y-%m-%d')
        title = [{"text": {"content": day_name}}]
        daydate = {"start": day_name}
        read_time = day_stat.day_read_time

        relations = []
        for book_id_ko in day_stat.read_books:
            relations.append({"id": koreader_notion_map[book_id_ko], "relation": {"database_id": nob.database_id}})

        day_page = self.notion.pages.create(
            **{
                "parent": {
                    "database_id": self.database_id,
                },
                "properties": {
                    "Day": {"title": title},
                    "Daydate": {"date": daydate},
                    "Read Seconds": {"number": read_time},
                    "Books Read": {"relation": relations},
                },
            }
        )

        print(day_name, "successfully added to notion")