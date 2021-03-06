import sqlite3
import os
import fnmatch
import datetime
import re
from src import jsoncall


class BuildDB:

    def __init__(self, name):
        self.path = '../db/'
        self.name = name
        self.filename = ""

    # Returns SQLite connection object for existing db
    # in /db/ directory, if none exist, creates new one
    def opendb(self):
        print("All pathnames relative to current working dir " + os.getcwd())
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.filename = self.path + self.name + "-" + timestamp + ".db"
        print("Created new db file " + self.filename)
        return sqlite3.connect(self.filename)

    def openspecdb(self, filename):
        print("All pathnames relative to current working dir " + os.getcwd())
        self.filename = filename
        print("Using existing db " + self.filename)
        return sqlite3.connect(self.filename)

    def createschema(self, connection):
        cursor = connection.cursor()
        # Video table
        cursor.execute('''
            CREATE TABLE Video(
            number INTEGER PRIMARY KEY ASC, 
            id TEXT UNIQUE, 
            title TEXT,
            channelid TEXT,
            jsondata TEXT,
            UNIQUE(id, jsondata),
            FOREIGN KEY (channelid) REFERENCES Channel(id))
            ;
        ''')
        # Channel table
        cursor.execute('''
            CREATE TABLE Channel(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT,
            jsondata TEXT,
            UNIQUE (id, jsondata))
            ;
            ''')
        # Playlist table
        cursor.execute('''
            CREATE TABLE Playlist(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT, 
            userid TEXT,
            jsondata TEXT,
            UNIQUE (id, jsondata),
            FOREIGN KEY (userid) REFERENCES Channel(id))
            ;''')
        # Comments table
        cursor.execute('''
            CREATE TABLE Comment(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT, 
            comment TEXT,
            userid TEXT,
            jsondata TEXT,
            UNIQUE (timestamp, vidid, comment, userid, jsondata),
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY (userid) REFERENCES Channel(id))
                    ''')
        # Watch events table
        cursor.execute('''
            CREATE TABLE Watch_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT, 
            channelid TEXT,
            userid TEXT,
            jsondata TEXT,
            UNIQUE(timestamp, vidid, channelid, userid, jsondata),
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
            jsondata TEXT,
            UNIQUE (timestamp, vidid, userid, playlistid, jsondata),
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
            jsondata TEXT,
            UNIQUE (timestamp, channelid, userid, jsondata),
            FOREIGN KEY(channelid) REFERENCES Channel(id),
            FOREIGN KEY (userid) REFERENCES Channel(id))''')
        connection.commit()
        print("Database schema created")

    # Shorten video URL into video ID
    def getvidid(self, url):
        if len(url) > 32:
            return url[32:]
        else:
            return url

    # Shorten video URL into video ID for comments
    def getvididcomment(self, url):
        if len(url) > 31:
            return url[31:]
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

    # Check if video exists in db
    def videoexists(self, vidid, connection):
        exists = False
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Video WHERE id = ?", (vidid,))
        if cursor.rowcount > 0:
            exists = True
        return exists, cursor.fetchone()

    # Count rows in table
    def countrows(self, tablename, connection):
        cursor = connection.cursor()
        selectstring = "SELECT count(*) FROM " + tablename
        cursor.execute(selectstring)
        return cursor.fetchone()

    # Insert into Channel table
    def channelinsert(self, cursor, channelid, name, jsondata):
        if not jsondata:
            statement = "INSERT OR IGNORE INTO Channel(id, name) VALUES(?,?)"
            cursor.execute(statement, (channelid, name))
        else:
            statement = "INSERT OR REPLACE INTO Channel(id, name, jsondata) VALUES(?,?,?)"
            cursor.execute(statement, (channelid, name, str(jsondata)))

    # Insert into Video table
    def videoinsert(self, cursor, videoid, title, channelid, jsondata):
        if not jsondata:
            statement = 'INSERT OR IGNORE INTO Video(id, title, channelid) VALUES(?, ?, ?)'
            cursor.execute(statement, (videoid, title, channelid))
        else:
            statement = 'INSERT OR REPLACE INTO Video(id, title, channelid, jsondata) VALUES(?, ?, ?, ?)'
            cursor.execute(statement, (videoid, title, channelid, str(jsondata)))
    # Insert into Playlist table
    def playlistinsert(self, cursor, playlistid, playlistname, userid, jsondata):
        if not jsondata:
            statement = "INSERT OR IGNORE INTO Playlist(id, name, userid) VALUES(?, ?, ?)"
            cursor.execute(statement, (playlistid, playlistname, userid))
        else:
            statement = "INSERT OR REPLACE INTO Playlist(id, name, userid, jsondata) VALUES(?, ?, ?, ?)"
            cursor.execute(statement, (playlistid, playlistname, userid, str(jsondata)))

    # Insert into Watch_Event table
    def watcheventinsert(self, cursor, timestamp, vidid, channelid, userid, jsondata):
        if not jsondata:
            statement = "INSERT OR IGNORE INTO Watch_Event(timestamp, vidid, channelid, userid) VALUES(?, ?, ?, ?)"
            cursor.execute(statement, (timestamp, vidid, channelid, userid))
        else:
            statement = "INSERT OR REPLACE INTO Watch_Event(timestamp, vidid, channelid, userid, jsondata) VALUES(?, ?, ?, ?, ?)"
            cursor.execute(statement, (timestamp, vidid, channelid, userid, str(jsondata)))

    # Insert into Playlist_Add_Event table
    def playlistaddinsert(self, cursor, timestamp, vidid, userid, playlistid, jsondata):
        if not jsondata:
            statement = "INSERT OR IGNORE INTO Playlist_Add_Event(timestamp, vidid, userid, playlistid) VALUES (?, ?, ?, ?)"
            cursor.execute(statement, (timestamp, vidid, userid, playlistid))
        else:
            statement = "INSERT OR REPLACE INTO Playlist_Add_Event(timestamp, vidid, userid, playlistid, jsondata) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(statement, (timestamp, vidid, userid, playlistid, str(jsondata)))

    # Scrape items from takeout 'watch-history.json' file into
    # SQLite db
    def scrapetakeoutwatch(self, inputreader, connection):
        cursor = connection.cursor()
        countbeginning = self.countrows("Watch_Event", connection)[0]
        for key in inputreader.keylists.keys():
            for item in inputreader.keylists.get(key):
                vidvalues = self.videoinsertvalues(item)
                chanvalues = self.channelinsertvalues(item)
                timestamp = item.get('time', '')
                self.channelinsert(cursor, chanvalues[0], chanvalues[1], None)
                self.videoinsert(cursor, vidvalues[0], vidvalues[1], chanvalues[0], None)
                self.watcheventinsert(cursor, timestamp, vidvalues[0], chanvalues[0], self.name, item)
        countend = self.countrows("Watch_Event", connection)[0]
        print("Inserted " + str(countend - countbeginning) + " rows into Watch_Event table")
        connection.commit()

    # Scrape items from a takeout playlist file into
    # SQLite db
    def scrapetakeoutplaylist(self, inputreader, connection):
        cursor = connection.cursor()
        countbeginning = self.countrows("Playlist_Add_Event", connection)
        # playlistnamere = re.search(re.compile(r"(.*\/).*"), inputreader.filename)
        playlistnamere = re.search(re.compile(r"[ \w-]+\."), inputreader.filename)
        if playlistnamere:
            playlistname = playlistnamere.group(0)[:-1]
        else:
            playlistname = inputreader.filename
        for item in inputreader.resultlist:
            vidid = item.get("contentDetails").get("videoId")
            vidtitle = item.get("snippet").get("title")
            timestamp = item.get("contentDetails").get("videoPublishedAt")
            # channelid, channelname is person who placed item in playlist
            channelid = item.get("snippet").get("channelId")
            channelname = item.get("snippet").get("channelTitle")
            playlistid = item.get("snippet").get("playlistId")
            self.channelinsert(cursor, channelid, channelname, None)
            # File does not contain the video's channel ID,
            # video will be inserted into table without channel ID
            cursor.execute('INSERT OR IGNORE INTO Video(id, title) VALUES(?, ?)', (vidid, vidtitle))
            self.playlistinsert(cursor, playlistid, playlistname, channelid, None)
            self.playlistaddinsert(cursor, timestamp, vidid, channelid, playlistid, item)
        countend = self.countrows("Playlist_Add_Event", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Playlist_Add_Event table")
        connection.commit()

    # Scrapes data from takeout 'subscriptions.json' file
    # into SQLite db
    def scrapetakeoutsubs(self, inputreader, connection):
        cursor = connection.cursor()
        cursor.execute("SELECT count(*) FROM Subscription_Add_Event")
        countbeginning = self.countrows("Subscription_Add_Event", connection)
        for item in inputreader.resultlist:
            userid = item.get("snippet").get("channelId")
            channelid = item.get("snippet").get("resourceId").get("channelId")
            channelname = item.get("snippet").get("title")
            timestamp = item.get("snippet").get("publishedAt")
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)', (channelid, channelname))
            cursor.execute('INSERT OR IGNORE INTO Subscription_Add_Event(timestamp, channelid, userid, jsondata) VALUES (?, ?, ?, ?)', (timestamp, channelid, userid, str(item)))
        countend = self.countrows("Subscription_Add_Event", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Subscription_Add_Event table")
        connection.commit()

    def scrapetakeoutcomments(self, inputreader, connection):
        cursor = connection.cursor()
        countbeginning = self.countrows("Comment", connection)
        userid = inputreader.userid
        username = inputreader.username
        for item in inputreader.resultlist:
            vidid = item.get("vidid")
            vidtitle = item.get("vidtitle")
            timestamp = item.get("timestamp")
            comment = item.get("comment")
            cursor.execute('INSERT OR IGNORE INTO Video(id, title) VALUES(?, ?)', (vidid, vidtitle))
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)', (userid, username))
            cursor.execute("INSERT OR IGNORE INTO Comment(timestamp, vidid, comment, userid) VALUES(?, ?, ?, ?)", (timestamp, vidid, comment, userid))
        countend = self.countrows("Comment", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Comment table")
        connection.commit()

    def scrapechannellisting(self, resultlist, connection):
        cursor = connection.cursor()
        countbeginning = self.countrows("Channel", connection)
        for item in resultlist:
            channelid = item.get("id")
            channelname = item.get("snippet").get("customUrl")
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name, jsondata) VALUES(?, ?, ?)', (channelid, channelname, str(item)))
        countend = self.countrows("Channel", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Channel table")
        connection.commit()

    def scrapeplaylistcontents(self, resultlist, connection, jsonquery):
        cursor = connection.cursor()
        countbeginning = self.countrows("Playlist_Add_Event", connection)
        playlistid = resultlist[0].get("snippet").get("playlistId")
        response = jsonquery.executerequest("playlistid", playlistid)
        playlistname = response.get("items")[0].get("snippet").get("title")
        for item in resultlist:
            vidid = item.get("contentDetails").get("videoId")
            vidtitle = item.get("snippet").get("title")
            vidresponse = jsonquery.executerequest("videoid", vidid)
            if vidresponse.get("items"):
                vidchannelid = vidresponse.get("items")[0].get("snippet").get("channelId")
            else:
                vidchannelid = ""
            timestamp = item.get("contentDetails").get("videoPublishedAt")
            channelid = item.get("snippet").get("channelId")
            channelname = item.get("snippet").get("channelTitle")
            playlistid = item.get("snippet").get("playlistId")
            cursor.execute('INSERT OR IGNORE INTO Channel(id, name) VALUES(?, ?)', (channelid, channelname))
            cursor.execute('INSERT OR IGNORE INTO Video(id, title, channelid, jsondata) VALUES(?, ?, ?, ?)', (vidid, vidtitle, vidchannelid, str(next(iter(vidresponse.get("items")), ""))))
            cursor.execute('INSERT OR IGNORE INTO Playlist(id, name, userid, jsondata) VALUES(?, ?, ?, ?)',
                           (playlistid, playlistname, channelid, str(next(iter(response.get("items")), ""))))
            cursor.execute(
                'INSERT OR IGNORE INTO Playlist_Add_Event(timestamp, vidid, userid, playlistid, jsondata) VALUES (?, ?, ?, ?, ?)',
                (timestamp, vidid, channelid, playlistid, str(item)))
        countend = self.countrows("Playlist_Add_Event", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Playlist_Add_Event table")
        connection.commit()

    def scrapevideoid(self, resultlist, connection):
        cursor = connection.cursor()
        countbeginning = self.countrows("Video", connection)
        for item in resultlist:
            if not self.videoexists(item.get("id"), connection)[0]:
                continue
            else:
                channelid = item.get("snippet").get("channelId")
                videoid = item.get("id")
                vidtitle = item.get("snippet").get("title")
                cursor.execute("INSERT OR IGNORE INTO Video(id, title, channelid, jsondata) VALUES(?, ?, ?, ?)", (videoid, vidtitle, channelid, str(item)))
        countend = self.countrows("Video", connection)
        print("Inserted " + str(countend[0] - countbeginning[0]) + " rows into Video table")
        connection.commit()
