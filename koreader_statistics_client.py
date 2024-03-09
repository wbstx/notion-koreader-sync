import sqlite3
import datetime

class KoreaderStatisticsClient:
    def __init__(self, database_path):
        self.database_path = database_path
        self.con = sqlite3.connect(database_path)
        self.cur = self.con.cursor()

        self.book_names = []
        self.author_names = []
        self.read_times = []

        self.num_of_books = self.load_books()

    def load_books(self):
        sql = 'select title, authors, total_read_time from book' 
        try: 
            self.cur.execute(sql) 
            book_all = self.cur.fetchall() 
            for p in book_all:
                self.book_names.append(p[0])
                self.author_names.append(p[1])
                self.read_times.append(p[2])
        except Exception as e: 
            print(e)
        finally: 
            self.cur.close() 
            self.con.close()
            return len(book_all)