import json
from bs4 import BeautifulSoup
from src import buildsqlitedb

class JsonReader:
    def __init__(self, filename):
        self.filename = filename
        # Stores dicts of JSON data parsed from input file
        self.resultlist = []
        self.readjsonfile()

    # Reads json file into self.resultlist dict
    def readjsonfile(self):
        with open(self.filename) as jsonfile:
            self.resultlist = json.load(jsonfile)


class WatchHistoryReader(JsonReader):

    def __init__(self, filename):
        JsonReader.__init__(self, filename)
        # Unique URL formats stored
        self.urltypes = set()
        # Dict with indexes of unique sets of JSON keys,
        # contents of which are the dicts of each JSON
        # with this key format
        self.keylists = {}
        self.fillkeylists()

    # Fills out keylists dict
    def fillkeylists(self):
        for item in self.resultlist:
            if tuple(item.keys()) not in self.keylists.keys():
                self.keylists[tuple(item.keys())] = []
            self.keylists[tuple(item.keys())].append(item)


class PlaylistReader(JsonReader):

    def __init__(self, filename):
        JsonReader.__init__(self, filename)
        self.playlistname = ""


class CommentReader:

    def __init__(self, filename, userid, username):
        self.resultlist = []
        self.userid = userid
        self.username = username
        with open(filename) as commenttext:
            soup = BeautifulSoup(commenttext)
        # vid = buildsqlitedb.BuildDB("vid")
        testlist = soup.findAll('li')
        counter = 0
        vid = buildsqlitedb.BuildDB("vid")
        for item in soup.findAll('li'):
            entry = {}
            counter += 1
            if item.contents[0] == "Commented on " and item.contents[1].attrs.get("href").startswith("http://www.youtube.com/watch?"):

                entry["vidid"] = vid.getvidid(item.contents[1].attrs.get("href"))
                entry["vidtitle"] = item.contents[1].text
                entry["timestamp"] = item.contents[2]
                entry["comment"] = item.contents[4]
            elif item.contents[0] == "Replied to a ":
                entry["vidid"] = vid.getvidid(item.contents[3].attrs.get("href"))
                entry["vidtitle"] = item.contents[3].text
                entry["timestamp"] = item.contents[4]
                entry["comment"] = item.contents[6]
            if entry:
                self.resultlist.append(entry)


    ''
