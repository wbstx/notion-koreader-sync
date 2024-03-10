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
    def get_day(self, day_stat):
        pass

    # https://developers.notion.com/reference/patch-page
    def update_day(self, day_stat):
        pass

    # https://developers.notion.com/reference/update-a-database
    def add_day(self, day_stat, koreader_notion_map):
        day_name = day_stat.day.strftime('%Y-%m-%d')
        title = [{"text": {"content": day_name}}]
        daydate = {"start": day_name}
        read_time = day_stat.day_read_time

        day_page = self.notion.pages.create(
            **{
                "parent": {
                    "database_id": self.database_id,
                },
                "properties": {
                    "Day": {"title": title},
                    "Daydate": {"date": daydate},
                    "Read Seconds": {"number": read_time},
                },
            }
        )

        print(day_name, "successfully added to notion")