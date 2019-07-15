import json

class InputReader:

    def __init__(self, filename):
        self.filename = filename
        self.resultlist = []

    def readjsonfile(self):
        with open(self.filename) as jsonfile:
            self.resultlist = json.load(jsonfile)

