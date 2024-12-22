from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import requests
from datetime import datetime, timedelta
from flask import Flask

# Bot token
BOT_TOKEN = "6893322008:AAGhwY02SakVAeXQVQrKk9ZGlF1goA_T8T4"

# Admin IDs
OWNER_ID = 6135934591
MAIN_ADMIN_ID = 6670048452
ADDITIONAL_ADMIN_ID = 7318766583
KAWIN = 6095233308

ADMIN_IDS = {OWNER_ID, MAIN_ADMIN_ID, ADDITIONAL_ADMIN_ID, KAWIN}

# Valid regions for requests
VALID_REGIONS = {"sg", "ind", "vn", "eu", "id", "bd", "ru", "th", "tw", "sac", "br", "na", "me", "pk"}

# Temporary storage
allowed_groups = set()
user_visits = {}  # Free usage data: {user_id: {'remaining': int, 'expires': datetime}}
user_spams = {}   # Free spam data: {user_id: {'remaining': int, 'expires': datetime}}
vip_users = {}    # VIP data: {user_id: {'visit_limit': int, 'spam_limit': int, 'days_left': int}}

# Initialize free user data
def initialize_user(user_id):
    today = datetime.now()
    if user_id not in user_visits or user_visits[user_id]['expires'] < today:
        user_visits[user_id] = {'remaining': 1, 'expires': today + timedelta(days=1)}
    if user_id not in user_spams or user_spams[user_id]['expires'] < today:
        user_spams[user_id] = {'remaining': 1, 'expires': today + timedelta(days=1)}

# Format time to "1234.00ms"
def format_time(total_seconds):
    return f"{total_seconds:.2f}ms"

# Handle /visit and /view commands
async def visit(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in allowed_groups:
        await update.message.reply_text(
            "Please join our group to interact with the bot seamlessly. Here's the link to join: https://t.me/freefirelikesvip"
        )
        return

    try:
        if len(context.args) != 2:
            await update.message.reply_text(
                "Please provide a valid region and a numeric UID.\nUsage: /View <region> <UID> Or\nUsage: /Visit <region> <UID>"
            )
            return

        region = context.args[0].lower()
        uid = context.args[1]

        if region not in VALID_REGIONS:
            await update.message.reply_text(f"Invalid region! Valid regions are: {', '.join(VALID_REGIONS).upper()}")
            return

        initialize_user(user_id)

        # Check free or VIP allowance
        if user_visits[user_id]['remaining'] <= 0:
            if user_id in vip_users and vip_users[user_id]['visit_limit'] > 0:
                vip_users[user_id]['visit_limit'] -= 1
            else:
                await update.message.reply_text(
                    "❌ Daily free visit limit exceeded and no VIP allowance left.\n\nOWNER - @MUKESHSARKAR69 ✔️\n"
                )
                return
        else:
            user_visits[user_id]['remaining'] -= 1  # Deduct free usage

        # Notify before processing
        await update.message.reply_text(f"🔄 Processing visit request for UID {uid} in region {region}...")

        # Send API request
        url = f"https://i5rk2k6jni.execute-api.ap-south-1.amazonaws.com/dev/api/{region}/{uid}/1000"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get('message') == "Requests processed successfully":
                formatted_time = f"{data.get('total_time', 0):.2f}ms"
                await update.message.reply_text(
                    f"✅ Visit request successful for UID {uid}. Total time: {formatted_time}. Please restart the game to check.\nOWNER - @MUKESHSARKAR69 ✔️\n"
                )
            else:
                await update.message.reply_text(f"API Error: {data.get('message')}")
        else:
            await update.message.reply_text(f"Failed to send request to API. Error code: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Add VIP users with limits
async def add_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    try:
        target_id = int(context.args[0])
        total_limit = int(context.args[1])

        if target_id not in vip_users:
            vip_users[target_id] = {
                'visit_limit': total_limit,
                'spam_limit': total_limit,
                'days_left': 30
            }
        else:
            vip_users[target_id]['visit_limit'] += total_limit
            vip_users[target_id]['spam_limit'] += total_limit

        await update.message.reply_text(
            f"User {target_id} has been granted {total_limit} total visits and spams for 30 days."
        )
    except Exception as e:
        await update.message.reply_text("Invalid command format. Usage: /add <user_id> <total_limit>")

# Handle spam requests
async def spam(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    initialize_user(user_id)

    if user_id in vip_users and vip_users[user_id]['spam_limit'] > 0:
        vip_users[user_id]['spam_limit'] -= 1
    elif user_spams[user_id]['remaining'] <= 0:
        await update.message.reply_text("❌ Daily free spam limit exceeded.")
        return
    else:
        user_spams[user_id]['remaining'] -= 1

    try:
        if len(context.args) != 1:
            await update.message.reply_text("Please provide a valid UID.\nUsage: /spam <UID>")
            return

        target_id = context.args[0]
        await update.message.reply_text(f"🔄 Processing spam request for UID {target_id}...")

        url = f"https://q17cfscmd6.execute-api.ap-south-1.amazonaws.com/spam/api/add/ind/MUKESH/{target_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get('message') == "Request processed successfully":
                await update.message.reply_text(
                    f"✅ Successfully sent 200 spam requests to UID {target_id}.\n\nOWNER - @MUKESHSARKAR69 ✔️\n"
                )
            else:
                await update.message.reply_text(f"API Error: {data.get('message')}")
        else:
            await update.message.reply_text(f"Failed to send spam request. Error code: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Check user limits
async def checkspam(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    initialize_user(user_id)

    if user_id in vip_users and vip_users[user_id]['days_left'] > 0:
        vip_info = vip_users[user_id]
        await update.message.reply_text(
            f"🔍 Your Status:\n"
            f"• User Type: VIP\n"
            f"• Daily Free Spam Requests Used: {1 - user_spams[user_id]['remaining']}/1\n"
            f"• Daily Free Visit Requests Used: {1 - user_visits[user_id]['remaining']}/1\n"
            f"• VIP Spam Requests Remaining: {vip_info['spam_limit']}\n"
            f"• VIP Visit Requests Remaining: {vip_info['visit_limit']}\n"
            f"• VIP Days Remaining: {vip_info['days_left']}\n\n"
            "OWNER - @MUKESHSARKAR69 ✔️\n"
            "JOIN MY GROUP - https://t.me/mukeshsarkar01\n"
        )
    else:
        await update.message.reply_text(
            f"🔍 Your Status:\n"
            f"• User Type: Free\n"
            f"• Daily Free Spam Requests Used: {1 - user_spams[user_id]['remaining']}/1\n"
            f"• Daily Free Visit Requests Used: {1 - user_visits[user_id]['remaining']}/1\n\n"
            "OWNER - @MUKESHSARKAR69 ✔️\n"
            "JOIN MY GROUP - https://t.me/mukeshsarkar01\n"
        )

# Allow group usage
async def allow(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    allowed_groups.add(chat_id)
    await update.message.reply_text("This group has been allowed to use the bot.")

# Flask application
app = Flask(__name__)

@app.route('/status')
def status():
    return "Bot is online"

# Main function
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("visit", visit))
    application.add_handler(CommandHandler("view", visit))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("spam", spam))
    application.add_handler(CommandHandler("checkspam", checkspam))
    application.add_handler(CommandHandler("allow", allow))

    # Run Flask app in a separate thread
    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=5000)
    
    thread = Thread(target=run_flask)
    thread.start()

    # Start bot
    application.run_polling()

if __name__ == '__main__':
    main()
