import os
import time
import json
from PIL import Image
from auth import authenticate
from image_utils import download_image, caption_image, ocr_image
from classifier import is_spam
from googleapiclient.errors import HttpError
import requests

PROCESSED_FILE = "processed.json"
IMAGE_FOLDER = "images"
CLEAN_ALBUM_TITLE = "Clean Album"
SPAM_ALBUM_TITLE = "Spam Album"

# ---------------- Album helpers ----------------
def create_album(service, title):
    result = service.albums().create(body={"album": {"title": title}}).execute()
    print(f"Created album: {result['title']} (ID: {result['id']})")
    return result['id']

def get_or_create_album(service, title):
    albums = service.albums().list(pageSize=50).execute().get("albums", [])
    for alb in albums:
        if alb["title"] == title:
            print(f"Found existing album: {title} (ID: {alb['id']})")
            return alb["id"]
    return create_album(service, title)

def add_photo_to_album(service, album_id, media_item_id):
    try:
        service.albums().batchAddMediaItems(
            albumId=album_id, body={"mediaItemIds": [media_item_id]}
        ).execute()
        print(f"Added photo {media_item_id} to album ID {album_id}")
    except HttpError as e:
        print(f"Failed to add photo to album: {e}")

# ---------------- Processed JSON ----------------
def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed(processed):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed), f)

# ---------------- Upload helper ----------------
def upload_image(service, creds, image_path, album_id):
    # Upload token
    with open(image_path, "rb") as img:
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-File-Name": os.path.basename(image_path),
            "X-Goog-Upload-Protocol": "raw",
        }
        r = requests.post("https://photoslibrary.googleapis.com/v1/uploads", headers=headers, data=img)
        if r.status_code != 200:
            print(f"Upload failed: {r.text}")
            return None
        upload_token = r.text

    # Create media item
    create_body = {
        "newMediaItems": [
            {"description": "Uploaded by Spam-Cleaner Bot",
             "simpleMediaItem": {"uploadToken": upload_token}}
        ]
    }
    r2 = requests.post(
        "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
        headers={"Authorization": f"Bearer {creds.token}", "Content-type": "application/json"},
        json=create_body
    )
    if r2.status_code == 200:
        media_item_id = r2.json()["newMediaItemResults"][0]["mediaItem"]["id"]
        # Add to album
        add_photo_to_album(service, album_id, media_item_id)
        return media_item_id
    else:
        print(f"Failed to create media item: {r2.text}")
        return None

# ---------------- Spam detection ----------------
def is_image_spam(image_path):
    mime = Image.open(image_path).format
    if mime.lower() == "gif":
        return True
    img = Image.open(image_path).convert("RGB")
    caption = caption_image(img)
    ocr_text = ocr_image(img)
    combined_text = caption + " " + ocr_text
    return is_spam(combined_text)

# ---------------- Main Loop ----------------
def main():
    service = authenticate()
    creds = service._http.credentials  # needed for upload headers

    clean_album_id = get_or_create_album(service, CLEAN_ALBUM_TITLE)
    spam_album_id = get_or_create_album(service, SPAM_ALBUM_TITLE)

    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    processed = load_processed()

    print("Bot started. Watching folder for new images...")
    while True:
        for filename in os.listdir(IMAGE_FOLDER):
            full_path = os.path.join(IMAGE_FOLDER, filename)
            if not os.path.isfile(full_path):
                continue
            if full_path in processed:
                continue

            print(f"Processing {filename}...")
            try:
                if is_image_spam(full_path):
                    print("🚫 Spam detected!")
                    upload_image(service, creds, full_path, spam_album_id)
                else:
                    print("✅ Clean image")
                    upload_image(service, creds, full_path, clean_album_id)
                processed.add(full_path)
                save_processed(processed)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        time.sleep(10)  # check every 10 seconds

if __name__ == "__main__":
    main()
