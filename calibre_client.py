import sqlite3
import datetime
import os

class CalibreClient:
    def __init__(self, root_path):
        self.root_path = root_path
        self.database_path = os.path.join(self.root_path, 'metadata.db')
        self.con = sqlite3.connect(self.database_path)
        self.cur = self.con.cursor()

    def get_cover_path_by_book_title(self, book_title, author_name=None):
        if author_name is None:
            book_string = "\"" + str(book_title) + "\""
            bookid_sql = f'select id, path from books where (title like {book_string})'
            # TODO: Double check author name
            try: 
                self.cur.execute(bookid_sql) 
                target_book = self.cur.fetchall()
                return os.path.join(self.root_path, target_book[0][1], 'cover.jpg')
            except Exception as e: 
                print(e)

    def destroy_sql_cursor(self):
        self.cur.close() 
        self.con.close()