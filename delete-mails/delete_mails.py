from googleapiclient.discovery import build
import base64
import email
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
#creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES = ['https://mail.google.com/']

TOKEN_FILE = 'token.pickle'

def authenticate_gmail(): 
    creds = None
    # Load existing credentials (if available)
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or missing, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Run authentication


#will list only one page 
def list_emails(service, query):
    
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new emails found ")
        return

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']

        for header in headers:
            if header['name'] == 'Subject':
                print(f"Subject: {header['value']}")


def delete_emails_one_page(service, filter_query):
    """Delete emails matching the filter."""
    results = service.users().messages().list(userId='me', q=filter_query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No matching emails found.")
        return

    for msg in messages:
        msg_id = msg['id']
        service.users().messages().delete(userId='me', id=msg_id).execute()
        print(f"Deleted email ID: {msg_id}")

# will delete all pages
def delete_filtered_emails(service, query):
    # Initialize pageToken for pagination
    print('Start Deleting...')

    page_token = None
    page_count = 0
    msg_count=0

    while True:
        # List messages matching the filter query
        results = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No matching emails found.")
            break

        for msg in messages:
            # Delete each message by ID
            msg_id = msg['id']
            try:
                #service.users().messages().delete(userId='me', id=msg_id).execute()
                msg_count = msg_count+1 
            except Exception as e:
                print(f"Failed to delete message with ID {msg_id}: {str(e)}")

        # Check for more pages
        
        page_token = results.get('nextPageToken')
        page_count = page_count+1          

        print(f'Deleted {page_count} pages, {msg_count} messages')    

        if not page_token:
            break  # No more pages, exit the loop

    
# Authenticate using OAuth
creds = authenticate_gmail()
service = build('gmail', 'v1', credentials=creds)
#query = "before:2023/01/01 -has:userlabels -is:important -is:starred"
query = "before:2023/01/01 -has:userlabels -is:starred"
#query = "before:2023/01/01"
delete_filtered_emails(service, query)
#list_emails(service, query)



