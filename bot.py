import os
import time
import requests

# Railway के एनवायरनमेंट वेरिएबल्स से सुरक्षित रूप से डेटा लेना
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
CUELINKS_API_KEY = os.environ.get('CUELINKS_API_KEY')

# डुप्लीकेट रोकने के लिए भेजी गई डील्स का रिकॉर्ड रखने की सेट (Set)
sent_deals = set()

def fetch_and_post_deals():
    # सुरक्षा जांच: अगर टोकन या की नहीं मिले तो बोट रुक जाएगा
    if not BOT_TOKEN or not CUELINKS_API_KEY or not CHAT_ID:
        print("त्रुटि: Railway में Variables (BOT_TOKEN, CHAT_ID, CUELINKS_API_KEY) सेट नहीं हैं!")
        return

    url = "https://links.cuelinks.com/api/v2/deals"
    headers = {
        "Authorization": f"Bearer {CUELINKS_API_KEY}",
        "Accept": "application/json"
    }
    
    print("स्मार्ट शॉपर्स बोट सफलतापूर्वक शुरू हो गया है और डील्स की तलाश कर रहा है...")
    
    while True:
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('deals', [])
                
                if not deals:
                    print("फिलहाल Cuelinks API से कोई नई डील नहीं मिली है।")
                
                for deal in deals:
                    deal_id = str(deal.get('id', ''))
                    title = deal.get('title', 'शानदार डील')
                    description = deal.get('description', '')
                    raw_url = deal.get('url', '')
                    store = deal.get('store', 'Shopping')
                    
                    # डुप्लीकेट प्रिवेंशन: अगर डील पहले नहीं भेजी गई है तभी आगे बढ़ेगा
                    if deal_id and deal_id not in sent_deals:
                        aff_url = f"https://links.cuelinks.com/url?u={raw_url}"
                        
                        message = (
                            f"🔥 **{title}** 🔥\n\n"
                            f"🛒 **Store:** {store}\n\n"
                            f"{description}\n\n"
                            f"👉 **खरीदने के लिए यहाँ क्लिक करें:**\n{aff_url}\n\n"
                            f"📢 Join @Smart Shoppers"
                        )
                        
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
                            if len(sent_deals) > 1000:
                                sent_deals.pop()
                        else:
                            print(f"टेलीग्राम पर भेजने में असफल: {tg_res.text}")
                            
                        time.sleep(5)
            else:
                print(f"Cuelinks API एरर: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"त्रुटि (Error) आई: {e}")
            
        print("अगली फेचिंग 15 मिनट बाद होगी...")
        time.sleep(900)

if __name__ == "__main__":
    fetch_and_post_deals()
    
