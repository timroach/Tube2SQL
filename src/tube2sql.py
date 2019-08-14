from src import takeout
from src import buildsqlitedb
from src import inputhandling
import sys
import argparse


def main():
    inputhandler = inputhandling.InputParseAndHandle()
    parser = inputhandler.create_parser()
    args = parser.parse_args()
    if args.subparser_name == 'takeout':
        inputhandler.scrapetakeout(args)
    argdict = vars(args)


if __name__ == '__main__':
    main()
