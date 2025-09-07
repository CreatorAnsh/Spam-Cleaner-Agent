import io
import requests
from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration

# BLIP model load karte hi (sirf pehli baar thoda heavy lagega)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def download_image(url):
    """
    Yeh function diya hua URL se image download karke PIL format me return karega.
    """
    response = requests.get(url)
    image = Image.open(io.BytesIO(response.content)).convert('RGB')
    return image

def ocr_image(image):
    """
    Yeh function image ke andar ka text (jo likha hua hai) padh lega.
    """
    return pytesseract.image_to_string(image)

def caption_image(image):
    """
    Yeh function image ka ek chhota sa caption banata hai
    (jaise 'a photo of a dog' ya 'poster with text').
    """
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption
