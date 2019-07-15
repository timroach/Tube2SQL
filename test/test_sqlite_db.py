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