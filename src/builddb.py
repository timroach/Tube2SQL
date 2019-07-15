import sqlite3
import os
import fnmatch
import datetime

class BuildDB:

    def __init__(self):
        self.path = '../db/'
        self.existingdbs = []
        for file in os.listdir(self.path):
            if fnmatch.fnmatch(file, '*.db'):
                self.existingdbs.append(file)

    # Returns SQLite connection object for existing db
    # in /db/ directory, if none exist, creates new one
    def opendb(self, name):
        if self.existingdbs:
            filename = self.existingdbs[0]
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = name + timestamp + ".db"
        return sqlite3.connect(filename)

