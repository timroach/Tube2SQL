# Tube2SQL
This is a tool for analyzing relationships between YouTube channels in terms of videos, playlists, subscriptions and comments made by and in between channels. This can be used to visualize activity relationships between users or channels, perform Social Network Analysis of selected targets, or cross-reference activity habits between users and/or channels. The data used to create the database comes from Google in JSON format, and can be obtained either through a request from takeout.google.com (with the options detailed below) or via the use of the YouTube Data API which is built into this tool. All that is required is a free Google Developer account, which is used to create an "OAuth client ID" and download a "Client Secrets JSON file" which should be placed in the root directory of the application (or it's path can be optionally specified by argument)

## Installation
This tool was developed on Ubuntu Linux, and while the path conventions used *should* be compatible with Windows pathnames, this has not yet been tested. To install the software, git clone the project to a local directory, then from the command line in the root directory, run `$ pip install -r requirements.txt` which should install all required package dependencies. 

## Before running for the first time
This tool relies on external sources of data to build up it's relational database, which must be aquired from takeout.google.com or pulled from YouTube's Data API using an appropriate developer account client secrets file (and an active internet connection). You should get one or both of these sources set up before you try to use the tool.
### Google Takeout
In a web browser, go to takeout.google.com, and scroll down to "Create a New Archive". Click on the "Deselect All" link, then scroll down to near the bottom of the page and check the box next to "YouTube". Click the button titled "All YouTube data included" and deselect everything except for history, my-comments, playlists, and subscriptions. It is important that you get all four of these, because certain information necessary to build the relational database is included in some of these files but not the others. Click OK to close the popup. Next, click on the "Multiple formats" button in the YouTube section, and select "JSON" for the watch-history entry (all others should be greyed out). Now, click on the "Next Step" button on the bottom right of the page. This will take you to the final page, which will as you to verify how you would like the archive delivered (defaults should be fine, you will be emailed a link to download a .zip file with the files). Once you receive this file (it may take a few minutes to an hour for the archive to be emailed to you), extract the complete folder structure including the "Takeout" folder into the `../tube2sql/inputfiles/` directory. If you don't do this, you will need to manually specify the path to the `Takeout` directory by argument.
### YouTube Data API
In a web browser, go to developer.google.com, and register for an account. Create a new project and name it whatever you would like. From the APIs and Services dashboard, click on the "Credentials" option in the left hand navigation pane. Click on the "Create credentials" dropdown button, and choose "OAuth client ID". Select "Web Application" and click the "Create" button. Once all the forms have been filled out, navigate back to the Credentials page, and under "OAuth 2.0 client IDs", your new credentials should appear. All the way on the right hand side, click on the pen icon to download your credentials file (client secrets JSON file). Place it in the root directory of the tool so it can be found automatically.

## Using the tool to relate Takeout data
If the Takeout files have been placed in the `inputfiles` directory, just running the command `tube2sql takeout` should process all of the files there and save the results in a SQLite database file in the `../tube2sql/db/` directory, with a filename composed of the username which is the owner of the 

## Author
Tim Roach

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
