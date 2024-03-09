import requests
import json
import logging
import notion_client
from notion_koreader_dataset_client import NotionDatabaseClient
from koreader_statistics_client import KoreaderStatisticsClient
import os
import re
from utils.bookinfo_format import author_name_format, seconds_to_hours_format

def export_koreader_to_notion(kos_db, notion_db):
    for i in range(kos_db.num_of_books):
        book_name, author_name, read_time = kos_db.book_names[i], kos_db.author_names[i], kos_db.read_times[i]
        author_name = author_name_format(author_name)
        read_time = seconds_to_hours_format(read_time)

        try:
            # Query book in notion database to check if it already exists or needs update 
            queried_book = notion_db.get_book(book_name, author_name)
            # Add a new book in the notion db
            if queried_book is None: 
                notion_db.add_book(book_name, author_name, read_time)
            else:
                page_id = queried_book["page_id"]

                # Update read time in notion
                if queried_book["read_time"] != read_time:
                    notion_db.update_book(page_id, book_name, author_name, read_time)
                else:
                    print(f"{book_name} by {author_name} not modified")

        except notion_client.APIResponseError as error:
            logging.error(f"Error when updating {book_name} by {author_name} to notion")
            logging.error(error)

if __name__ == "__main__":

    # notion integration secret token, book dataset id
    API_KEY = os.environ["NOTION_TOKEN"]
    DATABASE_ID = "36c28ecfc10a46df9121466ec27874eb"

    # initialize book database client
    notion_db = NotionDatabaseClient(DATABASE_ID, API_KEY)
    kos_db = KoreaderStatisticsClient("F:\\books\\database\\statistics2.sqlite3")

    # koreader_statistics_db.export_all_to_notion(notion_client)

    export_koreader_to_notion(kos_db, notion_db)

    # for block in iterate_paginated_api(notion.databases.query, database_id=DATABASE_ID):
    #     print(block)