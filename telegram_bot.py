import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
from database import add_product, get_user_products, delete_product
from scraper import get_web_data

load_dotenv()
TOKEN = os.getenv("bot_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Welcome_msg = """
<b>PRICE DROP TRACKER</b>
━━━━━━━━━━━━━━━━━━━━

Track prices. Get notified when they drop.

<b>How it works:</b>
1. Send a product link
2. Set your target price
3. Get pinged the moment it hits

<b>Commands:</b>
/track — start tracking a product
/list — see what you're tracking
/remove — stop tracking something
/help — show this message again

━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(Welcome_msg, parse_mode="HTML")

async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /track <url> <target_price> (currency is MAD)")
        return
        
    url = context.args[0]
    target_price = context.args[1]
    user_id = str(update.message.from_user.id)
    
    try:
        target_price = float(target_price)
    except ValueError:
        await update.message.reply_text("The target price must be a valid number!")
        return
    
    await update.message.reply_text("Fetching product details...")
    
    scraped_data = await get_web_data(url)
    
    if not scraped_data or scraped_data == "Not found!":
        await update.message.reply_text("Could not parse product data from this link.")
        return
        
    title = scraped_data["title"]
    current_price = scraped_data["price"]
    image_url = scraped_data["image"]
    
    is_saved = add_product(user_id, url, target_price)
    
    if is_saved:
        caption_text = (
            f"Saved successfully!\n\n"
            f"Title: {title}\n"
            f"Current Price: {current_price} DH\n"
            f"Target Price: {target_price} DH"
        )
        try:
            await update.message.reply_photo(photo=image_url, caption=caption_text)
        except Exception:
            await update.message.reply_text(caption_text)
    else:
        await update.message.reply_text("You are already tracking this exact link!")

async def handle_unknown_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command, please enter a valid command.")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    products = get_user_products(user_id)

    if not products:
        await update.message.reply_text("You are not tracking any products right now.")
        return
        
    message = "<b>Your Tracked Products:</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for item in products:
        item_id = item[0]
        url = item[1]
        target_price = item[2]
        message += f"<b>ID:</b> {item_id}\n"
        message += f"<b>Target:</b> {target_price} DH\n"
        message += f"<b>Link:</b> {url}\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n"
        
    await update.message.reply_text(message, parse_mode="HTML")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "Please enter the command like this:\n/remove <id> \nExample:\n/remove 2"
        )
        return  
        
    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("The ID must be a number!")
        return
        
    user_id = str(update.message.from_user.id)
    success = delete_product(product_id, user_id)
    
    if success:
        await update.message.reply_text(f"Product ID {product_id} has been removed from your list.")
    else:
        await update.message.reply_text("Product not found or it does not belong to you.")

if __name__ == "__main__":
    print("Bot is waking up...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("track", track_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("remove", delete_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_messages))
    print("Bot is online! Go text it on Telegram.")
    app.run_polling()