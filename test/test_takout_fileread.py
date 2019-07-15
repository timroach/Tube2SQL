import pytest
from src import takeout

test_files = {"../inputfiles/watch-history.json", "testtakeoutfile.json"}

# Tests all entries in JSON file have minimum set of
# properties per video
@pytest.mark.parametrize("test_file", test_files)
def test_file_import(test_file):
    testjsonfile = takeout.InputReader(test_file)
    testjsonfile.readjsonfile()
    testkeys1 = ["header", "title", "titleUrl", "subtitles", "time", "products"]
    testkeys2 = ['header', 'title', 'titleUrl', 'time', 'products']
    testkeys3 = ['header', 'title', 'time', 'products']

    def keyexists(dict, key):
        return key in dict.keys()

    for dictitem in testjsonfile.resultlist:
        for item in testkeys3:
            assert keyexists(dictitem, item)


