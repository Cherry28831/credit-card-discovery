from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    token_path = 'cloud/token.pickle'
    creds_path = 'cloud/credentials.json'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def scan_drive():
    try:
        service = authenticate()
        results = service.files().list(
            pageSize=100,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        drive_files = {}
        
        for file in files:
            if file['mimeType'] == 'text/plain' or 'log' in file['name'].lower():
                try:
                    content = service.files().get_media(fileId=file['id']).execute()
                    drive_files[f"gdrive://{file['name']}"] = content.decode('utf-8', errors='ignore')
                except:
                    pass
        
        return drive_files
    except:
        return {}
