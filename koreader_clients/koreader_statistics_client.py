import sqlite3
import datetime
from dataclasses import dataclass
from datetime import datetime
import sys
from utils.bookinfo_format import seconds_to_hours_format


@dataclass
class KoreaderBook:
    ko_id: int # unique id in koreader
    book_name: str
    author_name: str
    total_pages: int
    md5: str
    read_time: int
    read_pages: int

    start_read_time: datetime = datetime(9999, 12, 31, 23, 59, 59, 999999)
    last_read_time: datetime = datetime(1, 1, 1)
    current_page: int = 0

    read_pages_progress: float = 0.0 # progress based on read pages
    last_progress: float = 0.0 # progress based on the current reading page

class DayStat:
    def __init__(self, day):
        self.day = day
        self.read_books = set()

        self.day_read_time = 0

        self.hours_stats = {}
        for i in range(24):
            self.hours_stats[i] = 0

    def update_day_stat(self, book_id, start_hour, day_read_time):
        self.read_books.add(book_id)
        self.day_read_time += day_read_time
        self.hours_stats[start_hour] += day_read_time

class KoreaderStatisticsClient:
    def __init__(self, database_path):
        self.database_path = database_path
        self.con = sqlite3.connect(database_path)
        self.cur = self.con.cursor()

        self.books = {} # key using koreader book id
        self.day_statistics = {} # key using date
        self.num_of_books = self.load_books()

    def load_books(self):
        sql = 'select id, title, authors, pages, md5, total_read_time, total_read_pages from book' 
        try: 
            self.cur.execute(sql) 
            book_all = self.cur.fetchall() 
            for p in book_all:
                self.books[p[0]] = KoreaderBook(ko_id=p[0], book_name=p[1], author_name=p[2], total_pages=p[3], \
                                               md5=p[4], read_time=p[5], read_pages=p[6])
                self.books[p[0]].read_pages_progress = round(self.books[p[0]].read_pages / self.books[p[0]].total_pages, 2)
        except Exception as e: 
            print(e)
        finally: 
            return len(self.books)
        
    def load_time(self):
        sql = 'select id_book, start_time, duration, page, total_pages from page_stat_data'
        self.cur.execute(sql) 
        time_all = self.cur.fetchall() 
        for p in time_all:
            book_id, timestamp, duration, current_page, total_pages = p[0], p[1], p[2], p[3], p[4]
            timestamp = datetime.fromtimestamp(timestamp)

            # Calculate Day statistics
            day_key = timestamp.strftime('%Y-%m-%d')
            if day_key not in self.day_statistics.keys():
                self.day_statistics[day_key] = DayStat(timestamp.replace(hour=0, minute=0, second=0, microsecond=0))
            self.day_statistics[day_key].update_day_stat(book_id, timestamp.hour, duration)

            # Count start/time for each book
            if self.books[book_id].start_read_time > timestamp:
                self.books[book_id].start_read_time = timestamp

            if self.books[book_id].last_read_time < timestamp:
                self.books[book_id].last_read_time = timestamp

            # # Calc progress
            self.books[book_id].last_progress = round(current_page / total_pages, 2)
                
        # for b in self.books.values():
        #     print(f'Book {b.ko_id}: {b.book_name} ({b.author_name}), start from {b.start_read_time}, last read at {b.last_read_time}, progess: {"%.2f%%" % (b.read_pages / b.total_pages * 100)}')

    def destroy_sql_cursor(self):
        self.cur.close() 
        self.con.close()