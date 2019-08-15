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

    # Takes a channelid, returns list of API call results
    def channelidinfo(self, youtube, channelid):
        return youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channelid
        )

    # Takes a channel name, returns list of API call results
    def channelnameinfo(self, name):
        request = "request = youtube.channels().list part=\"snippet,contentDetails,statistics\",        forUsername=\"" + name + "\")"
        rawjson = self.executerequest(request)
        return json.load(rawjson)

    def executerequest(self, type, identifier):
        # Code adapted from sample provided at
        # developers.google.com/youtube/

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


        client_secrets_file = self.secretsfile

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials)

        if type is "channelid":
            response = self.channelidinfo(youtube, identifier).execute()

        return response

