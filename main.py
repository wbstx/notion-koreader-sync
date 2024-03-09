import requests
import json
import logging
import notion_client
from notion_book_client import NotionBookClient
from notion_statistics_client import NotionStatisticsClient
from koreader_statistics_client import KoreaderStatisticsClient
from calibre_client import CalibreClient
import os
import re
from utils.bookinfo_format import author_name_format, seconds_to_hours_format
import cv2
from pathlib import Path

def export_koreader_to_notion(kos, nob):
    for i in range(kos.num_of_books):
        book_name, author_name, read_time = kos.book_names[i], kos.author_names[i], kos.read_times[i]
        author_name = author_name_format(author_name)
        # read_time = seconds_to_hours_format(read_time)

        try:
            # Query book in notion database to check if it already exists or needs update 
            queried_book = nob.get_book(book_name, author_name)
            # Add a new book in the notion db
            if queried_book is None: 
                nob.add_book(book_name, author_name, read_time)
            else:
                page_id = queried_book["page_id"]

                # Update read time in notion
                if queried_book["read_time"] != read_time:
                    nob.update_book(page_id, book_name, author_name, read_time)
                else:
                    print(f"{book_name} by {author_name} not modified")

        except notion_client.APIResponseError as error:
            logging.error(f"Error when updating {book_name} by {author_name} to notion")
            logging.error(error)

if __name__ == "__main__":

    # notion integration secret token, book dataset id
    API_KEY = os.environ["NOTION_TOKEN"]
    BOOK_DATABASE_ID = "36c28ecfc10a46df9121466ec27874eb"
    STATISTICS_ID = "35c495aac5de41ecb2ecd7d83893f2f7"

    MAX_COVER_SIZE = 800

    # now = datetime.now()
    # year = now.year
    # month = now.month

    # print(year, month)

    # Load koreader statistics dataset
    kos = KoreaderStatisticsClient("F:\\books\\database\\statistics2.sqlite3")

    # # Load calibre database for book cover
    # calibre_root_path = "F:\Calibre"
    # cac = CalibreClient(calibre_root_path)

    # # Collecting covers
    # # Notion api does not allow to upload files, so we need to do it manually 
    # for book_name in kos.book_names:
    #     print(book_name)
    #     cover_path = cac.get_cover_path_by_book_name(book_name)
    #     cover_img = cv2.imread(cover_path)
    #     h, w = cover_img.shape[:2]
    #     if max(w, h) > MAX_COVER_SIZE:
    #         scale = MAX_COVER_SIZE / max(w, h)
    #         cover_img = cv2.resize(cover_img, None, fx=scale, fy=scale)
    #     img_path = os.path.join("covers", book_name + ".jpg").replace(":", "")
    #     cv2.imencode('.jpg', cover_img)[1].tofile(img_path)
    
    # cac.destroy()

    # # initialize notion book database client
    # nob = NotionBookClient(BOOK_DATABASE_ID, API_KEY)
    # # export_koreader_to_notion(kos, nob)

    # notion_statistics_db = NotionStatisticsClient(STATISTICS_ID, API_KEY)
    # notion_statistics_db.get_total_statistics()
    # notion_statistics_db.update_total(nob)