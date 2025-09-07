import os
import pickle
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PIL import Image
import shutil
from image_utils import caption_image, ocr_image
from classifier import is_spam

# ✅ Google Photos ke liye sahi permissions
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    "https://www.googleapis.com/auth/photoslibrary"
]

# 🔍 Yeh function check karega image spam hai ya nahi
def is_spam_image(image_path):
    image = Image.open(image_path).convert("RGB")
    caption = caption_image(image)
    ocr_text = ocr_image(image)
    combined_text = caption + " " + ocr_text
    return is_spam(combined_text)

# 🔑 Login to Google Photos
def login():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)
    return creds

# 📤 Upload image to Google Photos
def upload_image(image_path, creds):
    with open(image_path, "rb") as img:
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-File-Name": os.path.basename(image_path),
            "X-Goog-Upload-Protocol": "raw",
        }
        response = requests.post("https://photoslibrary.googleapis.com/v1/uploads", headers=headers, data=img)
    
    if response.status_code == 200:
        upload_token = response.text
        create_item_url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-type": "application/json",
        }
        json_body = {
            "newMediaItems": [
                {
                    "description": "Uploaded by Spam Cleaner",
                    "simpleMediaItem": {
                        "uploadToken": upload_token
                    }
                }
            ]
        }
        response = requests.post(create_item_url, headers=headers, json=json_body)
        if response.status_code == 200:
            print(f"✅ Uploaded: {os.path.basename(image_path)}")
        else:
            print(f"❌ Failed to create media item: {response.text}")
    else:
        print(f"❌ Upload failed: {response.text}")

# 🏠 Main Function
def main():
    creds = login()
    image_folder = "images"
    clean_folder = "clean_images"

    # Folder bana lena agar nahi hai
    os.makedirs(clean_folder, exist_ok=True)

    for image_file in os.listdir(image_folder):
        full_path = os.path.join(image_folder, image_file)

        if not os.path.isfile(full_path):  # skip non-image files
            continue

        if is_spam_image(full_path):
            print(f"🗑️ SPAM Detected: {image_file}")
        else:
            print(f"✅ CLEAN: {image_file}")
            # clean folder me copy karo
            shutil.copy(full_path, os.path.join(clean_folder, image_file))
            # aur upload karo Google Photos me
            upload_image(full_path, creds)

if __name__ == "__main__":
    main()
