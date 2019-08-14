from src import takeout
from src import buildsqlitedb
from src import inputhandling
import sys
import argparse


def create_parser():
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

def takeoutoption(args):

    if not args.directory:
        todir = '../inputfiles/'
    else:
        todir = args.directory
    dirreader = takeout.directoryreader(todir)
    filedict = dirreader.builddict()
    if (not filedict.get("subscriptions") or not filedict.get("playlists")) and not args.userid:
        sys.exit("No userid specified and no Takeout files provided which contain userid.\n Rerun with \"takeout -u <userid>\" option or ensure there is at least one playlist file or subcription file present in Takeout directory.")

    if not args.database:
        dbpath = "./db/"
    else:
        dbpath = args.database



def main():
    inputhandler = inputhandling.TakeoutScrape()
    parser = inputhandler.create_parser()
    args = parser.parse_args()
    if args.subparser_name == 'takeout':
        inputhandler.scrapetakeout(args)
    argdict = vars(args)


    print(args)


if __name__ == '__main__':
    main()
