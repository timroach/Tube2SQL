import pytest
from src import buildsqlitedb
import os
import fnmatch

@pytest.fixture()
def test_db():
    return buildsqlitedb.BuildDB("testname")

def test_db_file(test_db):
    connection = test_db.opendb()
    fileexists = False
    for file in os.listdir("../db/"):
        if fnmatch.fnmatch(file, test_db.name + '*.db'):
            fileexists = True
    assert fileexists
    os.remove('../db/' + test_db.filename)

def test_db_connection(test_db):
    connection = test_db.opendb()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test_table (test1 text, test2 text)")
    connection.commit()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'test_table'")
    connection.commit()
    tablestructure = cursor.fetchone()
    assert tablestructure[0] == "CREATE TABLE test_table (test1 text, test2 text)"
    os.remove('../db/' + test_db.filename)

def test_db_structure(test_db):
    connection = test_db.opendb()
    test_db.builddb(connection)
    cursor = connection.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Video';")
    connection.commit()
    videoresponse = cursor.fetchone()
    assert videoresponse[0] == '''CREATE TABLE Video(
            number INTEGER PRIMARY KEY ASC, 
            id TEXT UNIQUE, 
            title TEXT,
            channelid TEXT,
            FOREIGN KEY (channelid) REFERENCES Channel(id))'''
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Channel';")
    connection.commit()
    channelresponse = cursor.fetchone()
    assert channelresponse[0] == '''CREATE TABLE Channel(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT)'''
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Watch_Event';")
    connection.commit()
    watcheventresponse = cursor.fetchone()
    assert watcheventresponse[0] == '''CREATE TABLE Watch_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT, 
            channelid TEXT,
            userid TEXT,
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY (channelid) REFERENCES Channel(id))'''
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Playlist_Add_Event';")
    connection.commit()
    watcheventresponse = cursor.fetchone()
    assert watcheventresponse[0] == '''CREATE TABLE Playlist_Add_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidid TEXT,
            userid TEXT,
            playlistid TEXT,
            FOREIGN KEY(vidid) REFERENCES Video(id),
            FOREIGN KEY(userid) REFERENCES Channel(id),
            FOREIGN KEY (playlistid) REFERENCES Playlist(id))'''
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Subscription_Add_Event';")
    connection.commit()
    watcheventresponse = cursor.fetchone()
    assert watcheventresponse[0] == '''CREATE TABLE Subscription_Add_Event(
            number INTEGER PRIMARY KEY ASC,
            timestamp TEXT,
            channelid TEXT,
            userid TEXT,
            FOREIGN KEY(channelid) REFERENCES Channel(id),
            FOREIGN KEY (userid) REFERENCES Channel(id))'''
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'Playlist';")
    connection.commit()
    watcheventresponse = cursor.fetchone()
    assert watcheventresponse[0] == '''CREATE TABLE Playlist(
            number INTEGER PRIMARY KEY ASC,
            id TEXT UNIQUE,
            name TEXT)'''
    os.remove('../db/' + test_db.filename)

def test_get_vidid(test_db):
    assert test_db.getvidid("https://www.youtube.com/watch?v\u003dtestvidid1") == "testvidid1"

def test_get_chanid(test_db):
    assert test_db.getchanid("https://www.youtube.com/channel/testchannelid1") == "testchannelid1"

def test_vidinsertvalues(test_db):
    assert test_db.videoinsertvalues(
        { "header": "YouTube",
          "title": "Watched Test title 1",
          "titleUrl": "https://www.youtube.com/watch?v\u003dtestvidid1",
          "subtitles": [{
            "name": "Test channel 1",
            "url": "https://www.youtube.com/channel/testchannelid1"
          }],
          "time": "2019-07-14T16:35:31.366Z",
          "products": ["YouTube"]
        }) == ("testvidid1", "Test title 1")

def test_channelinsertvalues(test_db):
    assert test_db.channelinsertvalues({ "header": "YouTube",
      "title": "Watched Test title 1",
      "titleUrl": "https://www.youtube.com/watch?v\u003dtestvidid1",
      "subtitles": [{
        "name": "Test channel 1",
        "url": "https://www.youtube.com/channel/testchannelid1"
      }],
      "time": "2019-07-14T16:35:31.366Z",
      "products": ["YouTube"]
    }) == ("testchannelid1", "Test channel 1")


