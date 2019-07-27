import sqlite3
import os
import fnmatch
import datetime
import re


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
            channelid TEXT,
            FOREIGN KEY (channelid) REFERENCES Channel(id))
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
        # Playlist table
        cursor.execute('''
            CREATE TABLE Playlist(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT)
            ;''')
        # Watch events table
        cursor.execute('''
            CREATE TABLE Watch_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT, 
            channelid TEXT,
            userid TEXT,
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY (channelid) REFERENCES Channel(id));
            ''')
        # Like events table
        cursor.execute('''
            CREATE TABLE Playlist_Add_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT,
            userid TEXT,
            playlistid TEXT,
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY(userid) REFERENCES Channel(id),
            FOREIGN KEY (playlistid) REFERENCES Playlist(id));''')
        # Subscription events table
        cursor.execute('''
            CREATE TABLE Subscription_Add_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            channelid TEXT,
            userid TEXT,
            FOREIGN KEY(channelid) REFERENCES Channel(id),
            FOREIGN KEY (userid) REFERENCES Channel(id))''')
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

    # Extract video ID and title from json line
    def videoinsertvalues(self, jsonline):
        id = self.getvidid(jsonline.get('titleUrl', ''))
        title = self.gettitle(jsonline.get('title', ''))
        return id, title

    # Extract channel ID and name from json line
    def channelinsertvalues(self, jsonline):
        subtitlelist = jsonline.get('subtitles', '')
        if subtitlelist and len(subtitlelist) > 0:
            id = self.getchanid(subtitlelist[0].get('url', ''))
            name = subtitlelist[0].get('name', '')
            return id, name
        else:
            return '', ''

    # Scrape items from takeout 'watch-history.json' file into
    # SQLite db
    def scrapetakeoutwatch(self, inputreader, connection):
        cursor = connection.cursor()
        for key in inputreader.keylists.keys():
            for item in inputreader.keylists.get(key):
                vidvalues = self.videoinsertvalues(item)
                chanvalues = self.channelinsertvalues(item)
                timestamp = item.get('time', '')
                cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?,?)', chanvalues)
                cursor.execute('INSERT OR IGNORE INTO Video(id, title, channelid) VALUES(?, ?, ?)', (vidvalues[0], vidvalues[1], chanvalues[0]))
                cursor.execute('INSERT INTO Watch_Event(timestamp, vidid, channelid, userid) VALUES(?, ?, ?, ?)', (timestamp, vidvalues[0], chanvalues[0], self.name))
            connection.commit()

    # Scrape items from a takeout playlist file into
    # SQLite db
    def scrapetakeoutplaylist(self, inputreader, connection):
        cursor = connection.cursor()
        # playlistnamere = re.search(re.compile(r"(.*\/).*"), inputreader.filename)
        playlistnamere = re.search(re.compile(r"[ \w-]+\."), inputreader.filename)
        playlistname = ""
        if playlistnamere:
            playlistname = playlistnamere.group(0)[:-1]
        else:
            playlistname = inputreader.filename
        for item in inputreader.resultlist:
            vidid = item.get("contentDetails").get("videoId")
            vidtitle = item.get("snippet").get("title")
            timestamp = item.get("contentDetails").get("videoPublishedAt")
            channelid = item.get("snippet").get("channelId")
            channelname = item.get("snippet").get("channelTitle")
            playlistid = item.get("snippet").get("playlistId")
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)', (channelid, channelname))
            cursor.execute('INSERT OR IGNORE INTO Video(id, title, channelid) VALUES(?, ?, ?)', (vidid, vidtitle, channelid))
            cursor.execute('INSERT OR IGNORE INTO Playlist(id, name) VALUES(?, ?)', (playlistid, playlistname))
            cursor.execute('INSERT INTO Playlist_Add_Event(timestamp, vidid, userid, playlistid) VALUES (?, ?, ?, ?)', (timestamp, vidid, channelid, playlistid))
        connection.commit()

    # Scrapes data from takeout 'subscriptions.json' file
    # into SQLite db
    def scrapetakeoutsubs(self, inputreader, connection):
        cursor = connection.cursor()
        for item in inputreader.resultlist:
            userid = item.get("snippet").get("channelId")
            channelid = item.get("snippet").get("resourceId").get("channelId")
            channelname = item.get("snippet").get("title")
            timestamp = item.get("snippet").get("publishedAt")
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)', (channelid, channelname))
            cursor.execute('INSERT INTO Subscription_Add_Event(timestamp, channelid, userid) VALUES (?, ?, ?)', (timestamp, channelid, userid))
        connection.commit()
