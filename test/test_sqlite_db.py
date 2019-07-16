import pytest
from src import builddb
import os
import fnmatch


def test_db_file():
    test_db = builddb.BuildDB("testname")
    connection = test_db.opendb()
    fileexists = False
    for file in os.listdir("../db/"):
        if fnmatch.fnmatch(file, test_db.name + '*.db'):
            fileexists = True
    assert fileexists
    os.remove('../db/' + test_db.filename)

def test_db_connection():
    test_db = builddb.BuildDB("testname")
    connection = test_db.opendb()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test_table (test1 text, test2 text)")
    connection.commit()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'test_table'")
    connection.commit()
    tablestructure = cursor.fetchone()
    assert tablestructure[0] == "CREATE TABLE test_table (test1 text, test2 text)"
    os.remove('../db/' + test_db.filename)

def test_db_structure():
    test_db = builddb.BuildDB("testname")
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
            description TEXT)'''
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
            number INTERGER PRIMARY KEY ASC,
            timestamp TEXT,
            vidnumber INTEGER, 
            channelnumber INTEGER,
            FOREIGN KEY(vidnumber) REFERENCES Video(number),
            FOREIGN KEY (channelnumber) REFERENCES Channel(number))'''
    os.remove('../db/' + test_db.filename)
