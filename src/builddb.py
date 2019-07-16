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

    def builddb(self, connection):
        cursor = connection.cursor()
        # Video table
        cursor.execute('''
            CREATE TABLE Video(
            number INTEGER PRIMARY KEY ASC, 
            id TEXT UNIQUE, 
            title TEXT,
            description TEXT)
            ;
        ''')
        # Channel table
        cursor.execute('''
            CREATE TABLE Channel(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT)
            ;
            ''')
        # Watch events table
        cursor.execute('''
            CREATE TABLE Watch_Event(
            number INTERGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidnumber INTEGER, 
            channelnumber INTEGER,
            FOREIGN KEY(vidnumber) REFERENCES Video(number),
            FOREIGN KEY (channelnumber) REFERENCES Channel(number));
            ''')
        connection.commit()

