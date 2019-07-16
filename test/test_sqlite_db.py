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

