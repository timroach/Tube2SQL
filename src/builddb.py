import sqlite3
import os
import fnmatch
import datetime


class BuildDB:

    def __init__(self, name):
        self.path = '../db/'
        self.name = name
        self.filename = ""
        self.existingdbs = []
        for file in os.listdir(self.path):
            if fnmatch.fnmatch(file, name + '*.db'):
                self.existingdbs.append(file)

    # Returns SQLite connection object for existing db
    # in /db/ directory, if none exist, creates new one
    def opendb(self):
        if self.existingdbs:
            self.filename = self.existingdbs[0]
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.filename = self.path + self.name + timestamp + ".db"
        return sqlite3.connect(self.filename)

