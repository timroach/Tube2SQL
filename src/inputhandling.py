import sys
import os
import argparse
import re
from src import takeout, buildsqlitedb, jsoncall



class InputParseAndHandle:
    def __init__(self):
        self.database = buildsqlitedb.BuildDB("empty")

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

        parser_takeout.add_argument(
            '-un', '--username',
            type=str, required=False,
            help='Specify username of owner of Takeout file'
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
            '-chn', '--channelname',
            type=str, required=False,
            help='Get info on username/channelname'
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
            '-s', '--secrets',
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
        # Sanity check, this should not run if subparser_name is not 'takeout'
        if not args.subparser_name == 'takeout':
            sys.exit("Error, scrapetakeout somehow called without takeout arg")
        if not args.directory:
            todir = '../inputfiles/'
        else:
            todir = args.directory
        dirreader = takeout.directoryreader(todir)
        filedict = dirreader.builddict()
        # Get userid and username either from command line input or pull it from a playlist or subscription file
        userid = ''
        username = ''
        if (not filedict.get("subscriptions") or not filedict.get("playlists")) and not args.userid:
            sys.exit(
                "No userid specified and no Takeout files provided which contain userid.\n Rerun with \"takeout -u <userid>\" option or ensure there is at least one playlist file or subcription file present in Takeout directory.")
        if filedict.get("subscriptions"):

            subscriptions = takeout.JsonReader(filedict.get("subscriptions")).resultlist
            if subscriptions[0]:
                userid = subscriptions[0].get("snippet").get("channelId")
        if filedict.get("playlists"):
            for item in filedict.get("playlists"):
                if takeout.PlaylistReader(item).resultlist:
                    firstitem = takeout.PlaylistReader(item).resultlist[0]
                    if not userid:
                        userid = firstitem.get("snippet").get("channelId")
                    username = firstitem.get("snippet").get("channelTitle")
                    break
        if args.userid:
            userid = args.userid
        if args.username:
            username = args.username
        if not userid:
            sys.exit("No valid userid found in Takeout files and none specified in args.\n Rerun with \"takeout -u <userid>\" option or ensure there is at least one playlist file or subcription file present in Takeout directory.")
        if not username:
            sys.exit(
                "No valid username found in Takeout files and none specified in args.\n Rerun with \"takeout -un <username>\" option or ensure there is at least one playlist file present in Takeout directory.")
        # Create the DB object (file will be created automatically on first use)
        takeout_db = buildsqlitedb.BuildDB(userid)
        # If db file specified in args, open that
        if args.database:
            connection = takeout_db.openspecdb(args.database)
        # Otherwise, create new db and build schema
        else:
            connection = takeout_db.opendb()
            takeout_db.createschema(connection)
        self.database = takeout_db
        # add watch history to db
        if filedict.get("watch-history"):
            print("Adding watch history " + filedict.get("watch-history"))
            inputreader = takeout.WatchHistoryReader(filedict.get("watch-history"))
            takeout_db.scrapetakeoutwatch(inputreader, connection)
        # Step through each playlist, add each to db
        if filedict.get("playlists"):
            playlists = filedict.get("playlists")
            for item in playlists:
                print("Adding playlist" + item )
                inputreader = takeout.PlaylistReader(item)
                takeout_db.scrapetakeoutplaylist(inputreader, connection)
        # Add comments to db
        if filedict.get("my-comments"):
            print("Adding comments " + filedict.get("my-comments"))
            inputreader = takeout.CommentReader(filedict.get("my-comments"), userid, username)
            takeout_db.scrapetakeoutcomments(inputreader, connection)
        # Add subscriptions to db
        if filedict.get("subscriptions"):
            print("Adding subscriptions " + filedict.get("subscriptions"))
            inputreader = takeout.JsonReader(filedict.get("subscriptions"))
            takeout_db.scrapetakeoutsubs(inputreader, connection)

    def calljson(self, args):
        if not args.subparser_name == 'json':
            sys.exit("Error, json somehow called without json arg")
        # Get and load client secret file path
        secretfile = ""
        if args.secrets:
            secretfile = args.secrets
        else:
            pattern = re.compile(r"(client_secret_).*(json)")
            files = [f for f in os.listdir('..') if os.path.join('..', f)]
            for file in files:
                result = pattern.search(file)
                if result:
                    secretfile = os.path.join(os.path.abspath(".."), file)
                    break
        # If this point is reached, no secretfile was
        # provided and none was found in the
        # current dir, error and exit.
        if not secretfile:
            sys.exit("No Google API client secrets file specified, and none found in current directory.\nEnsure file exists and is named \"client_secret_....json\"\nTo obtain a client secrets file, register at developers.google.com and create and download an OAuth 2.0 client ID file from the Credentials console.")
        nameargs = [args.channelid, args.channelname, args.playlistid, args.videoid]
        # If 'json' called with no options
        if not any(nameargs):
            sys.exit("Must specify a videoid, playlistid, channelid, or channelname to pull JSON data.\nRerun with \'-chid\' <channelid>, \'-chn\' <channelname>, \'-plid\' <playlistid>, or \'-vid\' <videoid> arguments")
        # If called with at least one option, make that the db name
        else:
            for item in nameargs:
                if item:
                    dbname = item
                    break
        # Create the DB object (file will be created automatically on first use)
        json_db = buildsqlitedb.BuildDB(dbname)
        # If db file specified in args, open that
        if args.database:
            connection = json_db.openspecdb(args.database)
        # Otherwise, create new db and build schema
        else:
            connection = json_db.opendb()
            json_db.createschema(connection)
        self.database = json_db
        jsonquery = jsoncall.apiquery(secretfile)
        if args.channelid:
            response = jsonquery.executerequest("channelid", args.channelid)
            results = response.get("pageInfo").get("totalResults")
            if results < 1:
                sys.exit("Channel ID query returned 0 results from YouTube's API")
            else:
                json_db.scrapechannellisting(response.get("items"), connection)
