# Kuch common spam shabd (keywords)
SPAM_KEYWORDS = [
    'free', 'win', 'click', 'crypto', 'giveaway', 'subscribe',
    'poster', 'advertisement', 'deal', 'limited', 'offer', 'bonus',
    'discount', 'follow', 'link', 'join now'
]

def is_spam(text):
    """
    Yeh function check karta hai ki given text me koi spam keyword hai ya nahi.
    Agar hai -> return True (matlab spam hai).
    Agar nahi hai -> return False (matlab clean hai).
    """
    text = text.lower()
    for kw in SPAM_KEYWORDS:
        if kw in text:
            return True
    return False
