import requests
import json
import logging
import os
import re
import cv2
from pathlib import Path
import datetime

import notion_client
from notion_db_clients.notion_book_client import NotionBookClient
from notion_db_clients.notion_statistics_client import NotionStatisticsClient
from notion_db_clients.notion_diary_client import NotionDiaryClient
from notion_db_clients.notion_quote_client import NotionQuoteClient
from koreader_clients.koreader_statistics_client import KoreaderStatisticsClient
from calibre_client import CalibreClient
from quotes_loader import QuotesLoader

from utils.bookinfo_format import author_name_format, seconds_to_hours_format

def export_koreader_books_to_notion(kos, nob):
    koreader_notion_map = {} # Mapping between koreader book_id and notion page_id
    for book in kos.books.values():
        # book_title, author_name, read_time = book.book_title, book.author_name, book.read_time
        book.author_name = author_name_format(book.author_name)

        try:
            # Query book in notion database to check if it already exists or needs update 
            queried_book = nob.get_book(book.book_title, book.author_name)
            # Add a new book in the notion db
            if queried_book is None: 
                book_page = nob.add_book(book)
                if book_page is not None:
                    koreader_notion_map[book.ko_id] = book_page["page_id"]
            else:
                page_id = queried_book["page_id"]
                koreader_notion_map[book.ko_id] = page_id
                # Update read time in notion
                if queried_book["read_time"] != book.read_time and queried_book["status"] != "Completed":
                    nob.update_book(page_id, book)
                else:
                    print(f"{book.book_title} by {book.author_name} not modified")

        except notion_client.APIResponseError as error:
            logging.error(f"Error when updating {book.book_title} by {book.author_name} to notion")
            logging.error(error)

    return koreader_notion_map

def export_koreader_statistics_to_notion(kos, nod, nob, koreader_notion_map):
    only_update_from_last_day_to_today = True

    start_day = kos.day_statistics[min(kos.day_statistics.keys())].day

    if only_update_from_last_day_to_today:
        start_day = datetime.datetime.strptime(nod.get_last_day(), '%Y-%m-%d')
    today = datetime.datetime.today()

    for i in range((today - start_day).days + 1):
        day = start_day + i*datetime.timedelta(days=1)
        day_stat = kos.day_statistics[day.strftime('%Y-%m-%d')]

        page_id = nod.get_day(day.strftime('%Y-%m-%d'))
        if page_id is None:
            nod.add_day(day_stat, nob, koreader_notion_map)
        else:
            nod.update_day(page_id, day_stat, koreader_notion_map)

    # for day, day_stat in kos.day_statistics.items():

        # book_str = ""
        # for book_id in day_stat.read_books:
        #     book_str += f'{kos.books[book_id].book_title} '
        # print(day, ": ", day, seconds_to_hours_format(day_stat.day_read_time), book_str)

if __name__ == "__main__":

    # notion integration secret token, dataset ids
    API_KEY = os.environ["NOTION_TOKEN"]
    BOOK_DATABASE_ID = "36c28ecfc10a46df9121466ec27874eb"
    STATISTICS_DATABASE_ID = "35c495aac5de41ecb2ecd7d83893f2f7"
    DIARY_DATABASE_ID = "4c576409431948e29cbb75829ad836d6"
    QUOTE_DATABASE_ID = "46419c75f6ed4954997d2a13cf7ddc0c"

    MAX_COVER_SIZE = 800 # Max resolution of cover images

    # Load koreader statistics dataset
    kos = KoreaderStatisticsClient("F:\\books\\database\\statistics.sqlite3")
    kos.load_time()
    kos.destroy_sql_cursor()
    quo = QuotesLoader("F:\\books\\highlights", kos)

    # # # initialize notion book database client
    nob = NotionBookClient(BOOK_DATABASE_ID, API_KEY)
    koreader_notion_mapping = export_koreader_books_to_notion(kos, nob)

    noq = NotionQuoteClient(QUOTE_DATABASE_ID, API_KEY)

    for quote in quo.quotes.values():
        noq.add_quote(quote, nob, koreader_notion_mapping)

    nod = NotionDiaryClient(DIARY_DATABASE_ID, API_KEY)
    export_koreader_statistics_to_notion(kos, nod, nob, koreader_notion_mapping)

    notion_statistics_db = NotionStatisticsClient(STATISTICS_DATABASE_ID, API_KEY)
    notion_statistics_db.get_total_statistics()
    notion_statistics_db.update_total(nob)

    # Load calibre database for book cover
    calibre_root_path = "F:\Calibre"
    cac = CalibreClient(calibre_root_path)

    # Collecting covers
    # Notion api does not allow to upload files, so we need to do it manually 
    for book in kos.books.values():
        book_title = book.book_title
        print(book_title)
        cover_path = cac.get_cover_path_by_book_title(book_title)
        cover_img = cv2.imread(cover_path)
        h, w = cover_img.shape[:2]
        if max(w, h) > MAX_COVER_SIZE:
            scale = MAX_COVER_SIZE / max(w, h)
            cover_img = cv2.resize(cover_img, None, fx=scale, fy=scale)
        img_path = os.path.join("covers", book_title + ".jpg").replace(":", "")
        cv2.imencode('.jpg', cover_img)[1].tofile(img_path)
    
    cac.destroy_sql_cursor()