import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import magic
import click
import sys
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def format_link(fileId):
    return f"https://drive.google.com/file/d/{fileId}/view?usp=sharing"
@click.command()
@click.argument("filename")
def main(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)
    mimetype = magic.from_file(filename, mime=True)

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists("credentials.json"):
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            raise FileNotFoundError("credentials.json missing")
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    media_file = MediaFileUpload(filename, mimetype=mimetype)
    service = build("drive", "v3", credentials=creds)
    file = service.files().create(body = {"name":os.path.split(filename)[1]}, media_body=media_file, fields="id").execute()
    fileId=file["id"]
    permissions = service.permissions().create(fileId=fileId, body = {"type":"anyone", "role":"reader"}, fields="id").execute()
    print(format_link(fileId))
if __name__ == "__main__":
    main()
