import json

class InputReader:

    def __init__(self, filename):
        self.filename = filename
        # Stores dicts of JSON data parsed from input file
        self.resultlist = []
        # Unique URL formats stored
        self.urltypes = set()
        # Dict with indexes of unique sets of JSON keys,
        # contents of which are the dicts of each JSON
        # with this key format
        self.keylists = {}

    def readjsonfile(self):
        with open(self.filename) as jsonfile:
            self.resultlist = json.load(jsonfile)

    def fillkeylists(self):
        for item in self.resultlist:
            if tuple(item.keys()) not in self.keylists.keys():
                self.keylists[tuple(item.keys())] = []
            self.keylists[tuple(item.keys())].append(item)



