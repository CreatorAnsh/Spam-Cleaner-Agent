# Spam Cleaner Agent for Google Photos

A Python-based automation agent designed to maintain organization within Google Photos libraries. This tool automatically identifies and categorizes spam images—such as memes, GIFs, and images containing specific keywords—by moving them into a dedicated album, ensuring your primary photo feed remains clutter-free.

---

## Features

*   **Secure Authentication**: Implements the OAuth 2.0 protocol for secure, authorized access to the Google Photos API.
*   **Multi-Factor Spam Detection**:
    *   **Optical Character Recognition (OCR)**: Utilizes Tesseract to scan images for text and checks it against a configurable blocklist of keywords.
    *   **AI-Powered Image Captioning**: Employs the BLIP transformer model to generate descriptive captions for images, which are then analyzed for spam-like content.
    *   **File Type Filtering**: Automatically categorizes all GIF images as spam.
*   **Automated Library Management**:
    *   Creates and maintains two primary albums: **"Bot Watch"** (a log of all processed images) and **"Spam Album"**.
    *   Tracks processed media items using their unique ID to prevent redundant operations and API usage.
*   **Continuous Monitoring**: Operates as a daemon, polling the Google Photos library for new uploads at a configurable interval (default: 30 seconds).
*   **Pre-Upload Utility**: Includes a standalone script (`spam-cleaner.py`) for filtering local directories of images prior to uploading them to the cloud.

---

## Architecture and Components

The project is structured into several modules to separate concerns and promote maintainability:

*   **`agent.py`**: The primary service daemon. This script handles authentication, continuously monitors the user's Google Photos library for new media, and orchestrates the classification and organization process. It is designed for long-running, post-upload cleanup.

*   **`spam-cleaner.py`**: A standalone command-line utility. This script applies the same classification logic to images in a local file system directory, moving suspected spam into a local `./spam` folder. This is intended for pre-upload filtering.

*   **`auth.py`**: Manages the OAuth 2.0 flow, including token generation, refresh, and persistence to a `token.pickle` file.

*   **`classifier.py`**: Contains the core classification logic. This module integrates calls to OCR (via `image_utils.py`) and the BLIP model to determine if a given image meets the criteria for being classified as spam.

*   **`image_utils.py`**: Provides helper functions for image processing, including downloading media items from URLs, performing OCR, and handling image data for model inference.

---

## Installation and Setup

### Prerequisites

*   **Python 3.8+**
*   **Tesseract OCR Engine**: Must be installed system-wide.
    *   **Ubuntu/Debian:** `sudo apt install tesseract-ocr`
    *   **macOS:** `brew install tesseract`
    *   **Windows:** Download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/spam-cleaner-agent.git
cd spam-cleaner-agent
```
### 2. Configure a Python Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```
### 3. Install Python Dependencies
```
pip install -r requirements.txt
```
### 4. Configure Google API Credentials
1. Navigate to the Google Cloud Console.

2. Create a new project or select an existing one.

3. Enable the Google Photos Library API for your project.

4. Under APIs & Services > Credentials, create an OAuth 2.0 Client ID for a Desktop application.

5. Download the generated JSON credentials file.

6. Rename the file to credentials.json and place it in the root directory of this project.

7. Critical Security Note: The credentials.json file and the automatically generated token.pickle file contain sensitive authentication keys. They must be excluded from version control.

### Ensure your .gitignore file contains these entries
```
echo "credentials.json" >> .gitignore
echo "token.pickle" >> .gitignore
```
### Project Structure
```
spam-cleaner-agent/
├── agent.py                 # Main service daemon
├── spam-cleaner.py          # CLI for local image filtering
├── auth.py                  # Google OAuth2 authentication handling
├── classifier.py            # Spam classification logic (BLIP, keywords)
├── image_utils.py           # Utilities for image download and OCR
├── keywords.txt             # Configurable list of spam keywords
├── requirements.txt         # Project dependencies
├── .gitignore              # Specifies intentionally untracked files
├── credentials.json         # Google API credentials (DO NOT COMMIT)
└── token.pickle            # OAuth2 token cache (DO NOT COMMIT)
```
### Dependency
1. This project relies on the following key Python packages, detailed in requirements.txt:

2. pillow (PIL Fork): Image processing.

3. transformers (by Hugging Face): Provides the BLIP model.

4. torch (PyTorch): Machine learning framework for model inference.

5. pytesseract: Python wrapper for Tesseract-OCR.

6. google-auth, google-auth-oauthlib, google-api-python-client: Google API client libraries for authentication and Photos API interaction.

### Disclaimer
```
This project is an independent development and is not affiliated with, endorsed by, or supported by Google LLC. It utilizes the Google Photos API in compliance with its Terms of Service. Users are responsible for their own use of the API and should review all applicable terms and policies.
