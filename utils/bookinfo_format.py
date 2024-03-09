import re

def author_name_format(author_name):
    author_name = author_name.split("\n")[0]
    author_name = re.sub("\[.*?\]", "", author_name)
    author_name = re.sub("\(.*?\)""", "", author_name)
    author_name = author_name.replace(" ", "")
    return author_name

def seconds_to_hours_format(read_seconds):
    hours = read_seconds // 3600
    read_seconds %= 3600
    mins = read_seconds // 60
    read_seconds %= 60

    return "%dh %02dmin" % (hours, mins)