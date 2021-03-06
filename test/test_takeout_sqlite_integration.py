from src import buildsqlitedb, takeout
import pytest
import os


@pytest.fixture()
def test_db():
    return buildsqlitedb.BuildDB("testname")

def test_scrape_takeout_watch_history(test_db):
    connection = test_db.opendb()
    test_db.createschema(connection)
    inputreader = takeout.WatchHistoryReader("watch-history.json")
    test_db.scrapetakeoutwatch(inputreader, connection)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Watch_Event WHERE ROWID = 1")
    connection.commit()
    selection = cursor.fetchone()
    assert selection == (1, '2019-07-14T16:35:31.366Z', 'testvidid1', 'testchannelid1', 'testname')
    os.remove('../db/' + test_db.filename)

def test_watch_trial_run(test_db):
    connection = test_db.opendb()
    test_db.createschema(connection)
    inputreader = takeout.WatchHistoryReader("../inputfiles/watch-history.json")
    test_db.scrapetakeoutwatch(inputreader, connection)
    cursor = connection.cursor()
    os.remove('../db/' + test_db.filename)

def test_like_trial_run(test_db):
    connection = test_db.opendb()
    test_db.createschema(connection)
    inputreader = takeout.PlaylistReader("../inputfiles/Takeout/YouTube/playlists/likes.json")
    test_db.scrapetakeoutplaylist(inputreader, connection)
    os.remove('../db/' + test_db.filename)

def test_subs_trial_run(test_db):
    connection = test_db.opendb()
    test_db.createschema(connection)
    inputreader = takeout.JsonReader("../inputfiles/Takeout/YouTube/subscriptions/subscriptions.json")
    test_db.scrapetakeoutsubs(inputreader, connection)
    os.remove('../db/' + test_db.filename)

def test_comments_trial_run(test_db):
    connection = test_db.opendb()
    test_db.createschema(connection)
    inputreader = takeout.CommentReader("../inputfiles/Takeout/YouTube/my-comments/my-comments.html")
    buildsqlitedb.BuildDB.scrapetakeoutcomments(inputreader, connection)
    os.remove('../db/' + test_db.filename)

