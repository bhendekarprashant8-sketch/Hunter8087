import os
import time
import random
import requests

# पहले भेजी गई डील्स को याद रखने की लिस्ट ताकि डुप्लीकेट (एक ही डील बार-बार) न आए
posted_deal_ids = set()

def fetch_cuelinks_deals(api_key):
    url = "https://www.cuelinks.com/api/v2/deals.json"
    headers = {
        "Authorization": f"Token token={api_key}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("deals", [])
    except Exception as e:
        print("API फेच करने में एरर:", e)
    return []

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print("टेलीग्राम मैसेज भेजने में एरर:", e)
        return False

def main():
    # Render पर सेट किए गए एनवायरनमेंट वेरिएबल्स से सीधे डेटा उठाएगा (कोई इनपुट नहीं मांगेगा)
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    cuelinks_api_key = os.environ.get("CUELINKS_API_KEY")
    
    if not bot_token or not chat_id or not cuelinks_api_key:
        print("❌ जरूरी एनवायरनमेंट वेरिएबल्स सेट नहीं हैं! Render में जाकर चेक करें।")
        return

    print("🚀 हंटर 80 87 डील बोट लाइव हो गया है और काम कर रहा है!")
    
    while True:
        try:
            print("⏳ Cuelinks से नई और सस्ती डील्स की तलाश की जा रही है...")
            deals = fetch_cuelinks_deals(cuelinks_api_key)
            
            if deals:
                # ऐसी डील चुनें जो पहले पोस्ट न की गई हो
                fresh_deals = [d for d in deals if str(d.get("id")) not in posted_deal_ids]
                
                if not fresh_deals:
                    # अगर सारी दिख चुकी हैं, तो लिस्ट खाली करके फिर से नई डील्स लेंगे
                    posted_deal_ids.clear()
                    fresh_deals = deals
                
                deal = random.choice(fresh_deals)
                deal_id = str(deal.get("id", time.time()))
                title = deal.get("title", "महा बचत ऑफर")
                raw_url = deal.get("url", "https://www.amazon.in")
                aff_url = deal.get("affiliate_url", raw_url)
                
                message = (
                    f"🔥 **{title}**\n\n"
                    f"👉 **सबसे कम कीमत में खरीदने के लिए यहाँ क्लिक करें:**\n{aff_url}\n\n"
                    f"🛒 सीमित समय की डील - अभी ऑर्डर करें!"
                )
                
                if send_telegram_message(bot_token, chat_id, message):
                    posted_deal_ids.add(deal_id)
                    print("✅ नई डील सफलतापूपर्वक चैनल पर पोस्ट कर दी गई!")
                else:
                    print("⚠️ मैसेज भेजने में असफल, अगली बार कोशिश करेंगे।")
            else:
                print("⚠️ अभी कोई नई डील नहीं मिली, अगली बार कोशिश करेंगे।")
            
            # हर 15 से 20 मिनट का अंतराल ताकि चैनल पर स्पैम न हो और अलग-अलग डील्स मिलती रहें
            sleep_time = random.randint(900, 1200)
            print(f"⏳ अगली डील के लिए {sleep_time // 60} मिनट का इंतज़ार...")
            time.sleep(sleep_time)
            
        except Exception as e:
            print("लूप एरर:", e)
            time.sleep(60)

if __name__ == "__main__":
    main()
    
