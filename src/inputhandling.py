import sys
import argparse
from src import takeout, buildsqlitedb


class TakeoutScrape:
    def __init__(self):
        self.directory = ''
        self.database = ''

    def create_parser(self):
        parser = argparse.ArgumentParser(
            prog='tube2sql'
            # description="Create a relational database from YouTube Takeout data or JSON requests"
        )

        subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')

        # Takeout file subparser
        parser_takeout = subparsers.add_parser(
            'takeout',
            help='Import from Takeout folder in inputfiles directory'
        )

        parser_takeout.add_argument(
            '-d', '--directory',
            type=str, required=False,
            help='Specify location of Takeout directory'
        )

        parser_takeout.add_argument(
            '-u', '--userid',
            type=str, required=False,
            help='Specify userid of owner of Takeout file'
        )

        # JSON query subparser
        parser_json = subparsers.add_parser(
            'json',
            help='Pull data from YouTube\'s JSON API by channel ID or playlist'
        )

        parser_json.add_argument(
            '-chid', '--channelid',
            type=str, required=False,
            help='Get info on userid/channelid'
        )

        parser_json.add_argument(
            '-plid', '--playlistid',
            type=str, required=False,
            help='Specify playlist ID to get info on'
        )

        parser_json.add_argument(
            '-vid', '--videoid',
            type=str, required=False,
            help='Specify video ID to get info on'
        )

        parser_json.add_argument(
            '-s', '-secrets',
            type=str, required=False,
            help='Specify Google API secrets.json file to use for requests'
        )

        parser_json.add_argument(
            '-m', '--maxqueries',
            type=int, required=False,
            help='Max number of requests to query'
        )

        # ID fetcher subparser
        parser_id = subparsers.add_parser(
            'getid',
            help='Get ID from username, playlist URL, or video URL'
        )

        parser_id.add_argument(
            '-u', '-username',
            type=str, required=False,
            help='Username or channelname to get ID of'
        )

        parser_id.add_argument(
            '-p', '--playlisturl',
            type=str, required=False,
            help='Playlist URL to get ID of'
        )

        parser_id.add_argument(
            '-v', '--videourl',
            type=str, required=False,
            help='Video URL to get ID of'
        )

        # Global parser options
        parser.add_argument(
            '-db', '--database',
            type=str, required=False,
            help='Specify sqlite database file'
        )

        return parser

    def scrapetakeout(self, args):

        if not args.directory:
            todir = '../inputfiles/'
        else:
            todir = args.directory
        dirreader = takeout.directoryreader(todir)
        filedict = dirreader.builddict()
        # Get userid either from command line input or pull it from a playlist or subcription file
        if (not filedict.get("subscriptions") or not filedict.get("playlists")) and not args.userid:
            sys.exit(
                "No userid specified and no Takeout files provided which contain userid.\n Rerun with \"takeout -u <userid>\" option or ensure there is at least one playlist file or subcription file present in Takeout directory.")
        elif filedict.get("subscriptions"):
            subscriptions = takeout.JsonReader(filedict.get("subscriptions")).resultlist
            if subscriptions[0]:
                userid = subscriptions[0].get("snippet").get("channelId")
            else:
                userid = ""
        elif filedict.get("playlists"):
            userid = ""
            for item in takeout.PlaylistReader(filedict.get("playlists")).resultlist:
                if item:
                    userid = item.get("snippet").get("channelId")
                    break
        else:
            userid = args.userid
        if not userid:
            sys.exit("No valid userid found in Takeout files and none specified in args.\n Rerun with \"takeout -u <userid>\" option or ensure there is at least one playlist file or subcription file present in Takeout directory.")
        # Create the DB object (file will be created automatically on first use)
        takeout_db = buildsqlitedb.BuildDB(userid)
        # If db file specified in args, open that, otherwise, create new db
        if args.database:
            connection = takeout_db.openspecdb(args.database)
        else:
            connection = takeout_db.opendb()
        # Set up database
        takeout_db.builddb(connection)
        # add watch history to db
        if filedict.get("watch-history"):
            print("Adding watch history " + filedict.get("watch-history") + " to " + takeout_db.filename)
            inputreader = takeout.WatchHistoryReader(filedict.get("watch-history"))
            takeout_db.scrapetakeoutwatch(inputreader, connection)
        # Step through each playlist, add each to db
        if filedict.get("playlists"):
            playlists = filedict.get("playlists")
            for item in playlists:
                print("Adding playlist" + item + " to " + takeout_db.filename)
                inputreader = takeout.PlaylistReader(item)
                takeout_db.scrapetakeoutplaylist(inputreader, connection)
        # Add comments to db
        if filedict.get("my-comments"):
            print("Adding comments " + filedict.get("my-comments") + " to " + takeout_db.filename)
            inputreader = takeout.CommentReader(filedict.get("my-comments"))
            takeout_db.scrapetakeoutcomments(inputreader, connection)
        # Add subscriptions to db
        if filedict.get("subscriptions"):
            print("Adding subscriptions " + filedict.get("subscriptions") + " to " + takeout_db.filename)
            inputreader = takeout.JsonReader(filedict.get("subscriptions"))
            takeout_db.scrapetakeoutsubs(inputreader, connection)



