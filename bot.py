import os
import time
import requests
from threading import Thread
from flask import Flask

# 1. Render के पोर्ट एरर (No open ports detected) को रोकने के लिए डमी वेब सर्वर
app = Flask('')

@app.route('/')
def home():
    return "Hunter 80 87 Bot is Running Alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. Telegram और Cuelinks API की सेटिंग
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
CUELINKS_API_KEY = os.environ.get('CUELINKS_API_KEY')

# डुप्लीकेट रोकने के लिए भेजी गई डील्स का रिकॉर्ड रखने की लिस्ट
sent_deals = set()

def fetch_and_post_deals():
    url = "https://links.cuelinks.com/api/v2/deals"
    headers = {
        "Authorization": f"Bearer {CUELINKS_API_KEY}",
        "Accept": "application/json"
    }
    
    while True:
        try:
            print("Cuelinks API से नई डील्स फेच की जा रही हैं...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('deals', [])
                
                for deal in deals:
                    deal_id = str(deal.get('id', ''))
                    title = deal.get('title', 'शानदार डील')
                    description = deal.get('description', '')
                    raw_url = deal.get('url', '')
                    store = deal.get('store', 'Shopping')
                    
                    # अगर यह डील पहले नहीं भेजी गई है तभी आगे बढ़ेगा (डुप्लीकेट प्रिवेंशन)
                    if deal_id and deal_id not in sent_deals:
                        # एफिलिएट लिंक तैयार करना
                        aff_url = f"https://links.cuelinks.com/url?u={raw_url}"
                        
                        message = (
                            f"🔥 **{title}** 🔥\n\n"
                            f"🛒 **Store:** {store}\n\n"
                            f"{description}\n\n"
                            f"👉 **खरीदने के लिए यहाँ क्लिक करें:**\n{aff_url}\n\n"
                            f"📢 Join @Smart Shoppers"
                        )
                        
                        # टेलीग्राम पर मैसेज भेजना
                        tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        payload = {
                            "chat_id": CHAT_ID,
                            "text": message,
                            "parse_mode": "Markdown",
                            "disable_web_page_preview": False
                        }
                        
                        tg_res = requests.post(tg_url, json=payload)
                        if tg_res.status_code == 200:
                            print(f"सफलतापूर्वक पोस्ट किया गया: {title}")
                            sent_deals.add(deal_id)
                            # मेमोरी सुरक्षित रखने के लिए पुरानी लिस्ट को सीमित रखना
                            if len(sent_deals) > 1000:
                                sent_deals.pop()
                        else:
                            print(f"टेलीग्राम पर भेजने में असफल: {tg_res.text}")
                            
                        # हर डील भेजने के बीच थोड़ा गैप ताकि फ्लड न हो
                        time.sleep(5)
            else:
                print(f"Cuelinks API एरर: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"त्रुटि (Error) आई: {e}")
            
        # अगली बार डील्स चेक करने से पहले 15 मिनट (900 सेकंड) का इंतज़ार
        print("अगली फेचिंग 15 मिनट बाद होगी...")
        time.sleep(900)

if __name__ == "__main__":
    # पहले वेब सर्वर चालू करें ताकि Render का पोर्ट चेक पास हो जाए
    keep_alive()
    # फिर बैकग्राउंड में बोट का लूप शुरू करें
    fetch_and_post_deals()
    
