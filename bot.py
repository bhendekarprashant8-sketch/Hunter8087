import os
import time
import urllib.request
import json

# Railway के एनवायरनमेंट वेरिएबल्स से डेटा लेना
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
CUELINKS_API_KEY = os.environ.get('CUELINKS_API_KEY')

# डुप्लीकेट रोकने के लिए सेट
sent_deals = set()

def fetch_and_post_deals():
    if not BOT_TOKEN or not CUELINKS_API_KEY or not CHAT_ID:
        print("त्रुटि: Railway में Variables सेट नहीं हैं!")
        return

    url = "https://links.cuelinks.com/api/v2/deals"
    headers = {
        "Authorization": f"Bearer {CUELINKS_API_KEY}",
        "Accept": "application/json"
    }
    
    print("स्मार्ट शॉपर्स बोट सफलतापूर्वक शुरू हो गया है और डील्स की तलाश कर रहा है...")
    
    while True:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    deals = data.get('deals', [])
                    
                    if not deals:
                        print("फिलहाल Cuelinks API से कोई नई डील नहीं मिली है।")
                    
                    for deal in deals:
                        deal_id = str(deal.get('id', ''))
                        title = deal.get('title', 'शानदार डील')
                        description = deal.get('description', '')
                        raw_url = deal.get('url', '')
                        store = deal.get('store', 'Shopping')
                        
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
                            
                            data_bytes = json.dumps(payload).encode('utf-8')
                            tg_req = urllib.request.Request(tg_url, data=data_bytes, headers={'Content-Type': 'application/json'})
                            
                            try:
                                with urllib.request.urlopen(tg_req) as tg_res:
                                    if tg_res.status == 200:
                                        print(f"सफलतापूर्वक पोस्ट किया गया: {title}")
                                        sent_deals.add(deal_id)
                                        if len(sent_deals) > 1000:
                                            sent_deals.pop()
                            except Exception as tg_err:
                                print(f"टेलीग्राम पर भेजने में असफल: {tg_err}")
                                
                            time.sleep(5)
                else:
                    print(f"Cuelinks API एरर: {response.status}")
                
        except Exception as e:
            print(f"त्रुटि (Error) आई: {e}")
            
        print("अगली फेचिंग 15 मिनट बाद होगी...")
        time.sleep(900)

if __name__ == "__main__":
    fetch_and_post_deals()
    
