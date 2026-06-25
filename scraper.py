import os
import requests
from bs4 import BeautifulSoup

# टेलीग्राम सेटिंग्स
BOT_TOKEN = "8018701777:AAFYAaatZITotapFlLviVwLomzTMTiYxDx8"
CHAT_ID = "6057184049"
TARGET_URL = "https://sarkariresult.com.cm/"
DB_FILE = "sent_updates.txt"

def load_sent_updates():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_sent_update(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def scrape_website():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(TARGET_URL, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch website: {response.status_code}")
            return
    except Exception as e:
        print(f"Error connecting to website: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    sent_updates = load_sent_updates()
    
    # सेक्शन्स की लिस्ट जिन्हें ट्रैक करना है
    # यह कोड वेबसाइट के सभी लिंक्स (अधिसूचनाओं) को स्कैन करता है
    # आप इसे कस्टमाइज़ कर सकते हैं अगर वेबसाइट का ढांचा अलग हो
    blocks = soup.find_all("a")
    
    new_items_found = 0
    
    for block in blocks:
        title = block.text.strip()
        link = block.get("href", "")
        
        if not title or not link:
            continue
            
        if not link.startswith("http"):
            link = TARGET_URL + link

        # सिर्फ प्रासंगिक जॉब/रिजल्ट वाले लिंक्स को फिल्टर करने के लिए
        if "/latestjob/" in link or "/resulthome/" in link or "/admitcard/" in link or "/answerkey/" in link:
            if link not in sent_updates:
                # कैटेगरी पहचानना
                category = "🔔 अपडेट"
                if "/latestjob/" in link: category = "💼 New Job"
                elif "/resulthome/" in link: category = "📊 Result"
                elif "/admitcard/" in link: category = "🎟️ Admit Card"
                elif "/answerkey/" in link: category = "📝 Answer Key"

                message = f"✨ *{category}*\n\n📌 *Title:* {title}\n🔗 *Link:* [यहाँ क्लिक करें]({link})"
                send_telegram_message(message)
                save_sent_update(link)
                new_items_found += 1

    print(f"Scraping complete. Found {new_items_found} new updates.")

if __name__ == "__main__":
    scrape_website()
