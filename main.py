from database import get_all_products
from scraper import get_web_data
from telegram import Bot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("bot_TOKEN")

async def check_prices_and_notify():
    bot = Bot(token=TOKEN)
    
    while True:
        products = get_all_products()
        print(f"checking {len(products)} products...")
        
        for item in products:
            item_id = item[0]
            user_id = item[1]    # New: user_id is now at index 1
            url = item[2]        # New: url is now at index 2
            target_price = item[3] # New: target_price is now at index 3
            
            print(f"Checking ID {item_id} for user {user_id}...")
            scraped_data = await get_web_data(url)

            if not scraped_data or scraped_data == "Not found!":
                continue

            current_price = scraped_data["price"]
            title = scraped_data["title"]
            
            if current_price <= target_price:
                print(f"PRICE DROP DETECTED for {title}!")
                message = (
                    f"<b>PRICE DROP ALERT!</b>\n\n"
                    f"<b>Item:</b> {title}\n"
                    f"<b>Current Price:</b> {current_price} DH\n"
                    f"<b>Your Target:</b> {target_price} DH\n\n"
                    f"<b>Buy now:</b> {url}"
                )
                # Sends the alert directly to the user who tracked this specific item
                await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
                
            else:
                print(f"Price is still too high ({current_price} DH). Target is {target_price} DH.")
        
        print("Cycle complete. Sleeping for 1 hour...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(check_prices_and_notify())