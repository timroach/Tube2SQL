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
            title TEXT)
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
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT, 
            channelid TEXT,
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY (channelid) REFERENCES Channel(id));
            ''')
        connection.commit()

    # Shorten video URL into video ID
    def getvidid(self, url):
        if len(url) > 32:
            return url[32:]
        else:
            return url

    # Shorten channel URL into channel ID
    def getchanid(self, url):
        if len(url) > 32:
            return url[32:]
        else:
            return url

    # Removes 'Watched ' from beginning of every title
    def gettitle(self, title):
        if title.startswith("Watched https://www.youtube.com/watch?v="):
            return "No title available"
        if title.startswith('Watched a video that has been removed'):
            return "Video has been removed"
        if len(title) > 8:
            return title[8:]
        else:
            return title

    def videoinsertvalues(self, jsonline):
        id = self.getvidid(jsonline.get('titleUrl', ''))
        title = self.gettitle(jsonline.get('title', ''))
        return id, title

    def channelinsertvalues(self, jsonline):
        subtitlelist = jsonline.get('subtitles', '')
        if subtitlelist and len(subtitlelist) > 0:
            id = self.getchanid(subtitlelist[0].get('url', ''))
            name = subtitlelist[0].get('name', '')
            return id, name
        else:
            return '', ''

    def scrapetakeout(self, inputreader, connection):
        cursor = connection.cursor()
        for key in inputreader.keylists.keys():
            for item in inputreader.keylists.get(key):
                vidvalues = self.videoinsertvalues(item)
                chanvalues = self.channelinsertvalues(item)
                timestamp = item.get('time', '')
                cursor.execute('INSERT OR IGNORE INTO Video(id, title) VALUES(?,?)', vidvalues)
                cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?,?)', chanvalues)
                cursor.execute('INSERT INTO Watch_Event(timestamp, vidid, channelid) VALUES(?, ?, ?)',
                                   (timestamp, vidvalues[0], chanvalues[0]))
            connection.commit()
