import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Photos ke liye access permission (scopes)
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"
]


def authenticate():
    creds = None
    # Agar token.pickle file already hai (pehle login kiya tha), use load karo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Agar login details valid nahi hai to naya login karvao
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)  # browser khulega login ke liye
        print("✅ Login successful!")

        # Future ke liye creds save kar do
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Google Photos ka service object banao
    service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    return service

if __name__ == "__main__":
    service = authenticate()
    print("🎉 Authentication successful! Ready to use Google Photos API")
