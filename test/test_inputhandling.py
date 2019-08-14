import pytest, argparse, sys, os
from src import inputhandling

# List of potential valid tube2sql takeout args passed to inputhandling.py
test_takeout_good_args = [
    argparse.Namespace(
        database=None,
        directory='./Takeout Test Files/',
        subparser_name='takeout',
        userid=None,
        username=None),
    argparse.Namespace(
        database=None,
       directory='./Takeout Test Files/',
       subparser_name='takeout',
       userid='testuserid',
       username=None),
    ]

test_takeout_bad_args = [
    argparse.Namespace(
        database=None,
        directory=None,
        subparser_name=None,
        userid=None,
        username=None),
    ]

# Just tests that nothing crashes when tests are called with good args on valid test data.
@pytest.mark.parametrize("test_args", test_takeout_good_args)
def test_takout_scrape(test_args):
    inputhandler = inputhandling.TakeoutScrape()
    inputhandler.scrapetakeout(test_args)
    dbpath = inputhandler.database.filename
    os.remove(dbpath)

@pytest.mark.parametrize("test_args", test_takeout_bad_args)
def test_takout_scrape(test_args):
    inputhandler = inputhandling.TakeoutScrape()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        inputhandler.scrapetakeout(test_args)
    assert pytest_wrapped_e.type == SystemExit

