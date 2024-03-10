import sqlite3
import datetime
from dataclasses import dataclass
from datetime import datetime
import sys
from utils.bookinfo_format import seconds_to_hours_format


@dataclass
class KoreaderBook:
    id_ko: int # unique id in koreader
    book_name: str
    author_name: str
    total_pages: int
    md5: str
    read_time: int
    read_pages: int

    start_read_time: datetime = datetime(9999, 12, 31, 23, 59, 59, 999999)
    last_read_time: datetime = datetime(1, 1, 1)
    current_page: int = 0

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
                self.books[p[0]] = KoreaderBook(id_ko=p[0], book_name=p[1], author_name=p[2], total_pages=p[3], \
                                               md5=p[4], read_time=p[5], read_pages=p[6])
        except Exception as e: 
            print(e)
        finally: 
            return len(self.books)
        
    def load_time(self):
        sql = 'select id_book, start_time, duration from page_stat_data'
        self.cur.execute(sql) 
        time_all = self.cur.fetchall() 
        for p in time_all:
            timestamp = p[1]
            timestamp = datetime.fromtimestamp(timestamp)

            # Calculate Day statistics
            day_key = timestamp.strftime('%Y-%m-%d')
            if day_key not in self.day_statistics.keys():
                self.day_statistics[day_key] = DayStat(day_key)
            self.day_statistics[day_key].update_day_stat(p[0], timestamp.hour, p[2])

            # Count start/time for each book
            if self.books[p[0]].start_read_time > timestamp:
                self.books[p[0]].start_read_time = timestamp

            if self.books[p[0]].last_read_time < timestamp:
                self.books[p[0]].last_read_time = timestamp

        for day in self.day_statistics.values():
            book_str = ""
            for book_id in day.read_books:
                book_str += f'{self.books[book_id].book_name} '
            print(day.day, ": ", seconds_to_hours_format(day.day_read_time), book_str)

        for b in self.books.values():
            print(f'Book {b.id_ko}: {b.book_name} ({b.author_name}), start from {b.start_read_time}, last read at {b.last_read_time}')

    def destroy_sql_cursor(self):
        self.cur.close() 
        self.con.close()