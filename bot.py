import os
import json
import time
import requests

CONFIG_FILE = "bot_config.json"

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    
    print("\n--- 🤖 टेलीग्राम डील बॉट सेटअप ---")
    bot_token = input("1. अपना Telegram Bot Token यहाँ डालें: ").strip()
    chat_id = input("2. अपने चैनल का यूजरनेम (जैसे @smartshopper_store) डालें: ").strip()
    earnkaro_pid = input("3. अपनी EarnKaro ID डालें: ").strip()
    
    config = {
        "bot_token": bot_token,
        "chat_id": chat_id,
        "earnkaro_pid": earnkaro_pid
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    
    print("\n✅ जानकारी सफलतापूर्वक सेव हो गई है!\n")
    return config

def main():
    config = get_config()
    print("बोट शुरू हो गया है और चैनल पर टेस्ट मैसेज भेजा जा रहा है...")
    
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
    payload = {
        "chat_id": config['chat_id'],
        "text": "🎉 बधाई हो! आपका टेलीग्राम एफिलिएट डील बोट सफलतापूर्वक लाइव हो गया है!",
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        print("रिस्पॉन्स:", response.json())
    except Exception as e:
        print("एरर:", e)

if __name__ == "__main__":
    main()
