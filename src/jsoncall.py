import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class apiquery:
    def __init__(self, secretsfile):
        self.secretsfile = secretsfile
        self.api_service_name = "youtube"
        self.api_version = "v3"
        # Code adapted from sample provided at
        # developers.google.com/youtube/

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.client_secrets_file = self.secretsfile

        # Get credentials and create an API client
        self.flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, scopes)
        self.credentials = self.flow.run_console()
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=self.credentials)

    # Takes a channelid, returns list of API call results
    def channelidinfo(self, youtube, channelid):
        return youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channelid,
            maxResults=1
        )

    # Takes a channel name, returns list of API call results
    def channelnameinfo(self, youtube, channelname):
        return youtube.channels().list(
            part="snippet,contentDetails,statistics",
            forUsername=channelname,
            maxResults=1
        )

    # Takes a playlistID, returns info about playlist
    def playlistid(self, youtube, playlistid):
        return youtube.playlists().list(
            part="snippet,contentDetails",
            id=playlistid,
            maxResults=1
        )

    # Takes a playlistID, returns list of videos in playlist
    def playlistidvids(self, youtube, playlistid):
        return youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlistid,
            maxResults=50
        )

    # Takes a videoID, returns info on video
    def videoid(self, youtube, videoid):
        return youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=videoid,
            maxResults=1
        )

    def executerequest(self, type, identifier):


        if type is "channelid":
            response = self.channelidinfo(self.youtube, identifier).execute()
        elif type is "channelname":
            response = self.channelnameinfo(self.youtube, identifier).execute()
        elif type is "playlistid":
            response = self.playlistid(self.youtube, identifier).execute()
        elif type is "playlistiditems":
            response = self.playlistidvids(self.youtube, identifier).execute()
        elif type is "videoid":
            response = self.videoid(self.youtube, identifier).execute()
        else:
            response = None

        return response

