import json


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


class LikeHistoryReader(JsonReader):

    def __init__(self, filename):
        JsonReader.__init__(self, filename)
        self.likelist = []
