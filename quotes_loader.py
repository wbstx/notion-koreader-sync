import json
import glob
import os

class QuotesLoader:
    def __init__(self, quotes_folder_path):
        self.quotes_folder_path = quotes_folder_path
        self.json_files = glob.glob(os.path.join(self.quotes_folder_path, "*.json"))
        self.load_quotes()
    
    def load_quotes(self):
        for json_file in self.json_files:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
            print(data.keys())
            if "documents" in data.keys():
                print(data["documents"][0].keys())