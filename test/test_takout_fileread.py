import pytest
from src import takeout

# List of .json files to test
test_files = {"../inputfiles/watch-history.json", "testtakeoutfile.json"}

# Tests all entries in test_files produce a
# JSON file with the minimum set of properties per video
@pytest.mark.parametrize("test_file", test_files)
def test_file_import(test_file):
    testjsonfile = takeout.WatchHistoryReader(test_file)
    testjsonfile.readjsonfile()
    testjsonfile.fillkeylists()
    # Three possible sets of dict keys for each JSON watch history entry
    testkeys = [
        # Set 1 is full set with all properties
        ("header", "title", "titleUrl", "subtitles", "time", "products"),
        # Set 2 is for videos which are "unavailable", only URL and timestamp are stored
        ('header', 'title', 'titleUrl', 'time', 'products'),
        # Set 3 is for videos which have been removed
        ('header', 'title', 'time', 'products')]

    def keyexists(dict, key):
        return key in dict.keys()

    keysgood = False
    for item in testkeys:
        if keyexists(testjsonfile.keylists, item):
            keysgood = True
    assert keysgood


