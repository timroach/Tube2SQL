import json

class findrecorddicts:

    def __init__(self, filename):
        self.filename = filename
        self.resultlist = []
        self.keysets = set()
        self.urltypes = set()
        self.minkeyset = []
        self.midkeyset = []
        self.maxkeyset = []

    def readfile(self):
        with open(self.filename) as jsonfile:
            resultlist = json.load(jsonfile)
        for item in resultlist:
            dictkeys = item.keys()
            self.keysets.add(tuple(dictkeys))
            if list(dictkeys) == ['header', 'title', 'time', 'products']:
                self.minkeyset.append(item)
            elif list(dictkeys) == ['header', 'title', 'titleUrl', 'time', 'products']:
                self.midkeyset.append(item)
            elif list(dictkeys) == ["header", "title", "titleUrl", "subtitles", "time", "products"]:
                self.maxkeyset.append(item)


findobj = findrecorddicts('../inputfiles/watch-history.json')
findobj.readfile()
resultsset = findobj.resultlist
print(resultsset)
