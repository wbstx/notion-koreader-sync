import json
import glob
import os
from dataclasses import dataclass
from datetime import datetime
from utils.bookinfo_format import author_name_format, seconds_to_hours_format

# koreader highlights json format:
# single document: dict_keys(['md5sum', 'entries', 'author', 'version', 'created_on', 'file', 'title'])
# multiple documents: dict_keys(['created_on', 'documents', 'version'])
# each: dict_keys(['author', 'file', 'md5sum', 'entries', 'title'])
# entries: dict_keys(['time', 'drawer', 'sort', 'page', 'text', 'chapter'])

@dataclass
class Quote:
    ko_id: int
    book_title: str
    author_name: str
    create_time: datetime
    text: str
    chapter: str

class QuotesLoader:
    def __init__(self, quotes_folder_path, kos):
        self.quotes_folder_path = quotes_folder_path
        self.json_files = glob.glob(os.path.join(self.quotes_folder_path, "*.json"))
        self.quotes = {} # key: create_time
        self.load_quotes(kos)
    
    def load_quotes(self, kos):
        for json_file in self.json_files:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
            # Multiple documents
            # all_quotes_json = 
            all_quotes_json = data["documents"] if "documents" in data.keys() else [data]
            for doc in all_quotes_json:
                for quote_json in doc["entries"]:
                    if quote_json["time"] not in self.quotes.keys():
                        ko_book = list(filter(lambda x: x.book_title==doc["title"] \
                                    and x.author_name==doc["author"], kos.books.values()))
                        if len(ko_book) < 0:
                            print("quote from", self.quotes[quote_json["time"]].book_title, "is not matching with any book in the statistic db")
                        else:
                            self.quotes[quote_json["time"]] = Quote(ko_id=ko_book[0].ko_id, book_title=doc["title"], author_name=doc["author"], \
                                                                    create_time=datetime.fromtimestamp(quote_json["time"]), \
                                                                    chapter=quote_json["chapter"] ,text=quote_json["text"])

        print(len(self.quotes), "quotes loaded")

    def print_quotes(self):
        for time, quote in self.quotes.items():
            print(time, quote.text, "by", quote.author_name, "in", quote.book_title, "chapter", quote.chapter, "at", quote.create_time)
