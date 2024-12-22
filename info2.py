from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackContext, filters
from flask import Flask, jsonify
import threading
import asyncio

# Bot token
BOT_TOKEN = "6733571799:AAEScBTTuYNmCOKhzgk3jpRqQqPe783NvmU"

# Allowed user IDs (replace with the correct user IDs)
ALLOWED_USER_IDS = [7318766583, 6667256453, 6095233308]

# Flask app initialization
app = Flask(__name__)

# Function to filter and delete messages in the channel after 30 seconds
async def filter_channel_posts(update: Update, context: CallbackContext):
    # Ensure the bot is reacting to channel posts (messages in the channel)
    if update.channel_post:
        # Check if the post is from a user or a channel
        if update.channel_post.from_user:
            # If the message is from a user
            user_id = update.channel_post.from_user.id
        elif update.channel_post.sender_chat:
            # If the message is from a channel (admin)
            user_id = update.channel_post.sender_chat.id
        else:
            # If the message has no sender (this should not happen)
            return
        
        # If the user is not in the allowed list, delete the message immediately
        if user_id not in ALLOWED_USER_IDS:
            await context.bot.delete_message(
                chat_id=update.channel_post.chat_id,
                message_id=update.channel_post.message_id
            )
            print(f"Deleted message from user ID {user_id}")

        # Wait 30 seconds before deleting the message if it's not from an allowed user
        if user_id not in ALLOWED_USER_IDS:
            await asyncio.sleep(30)
            await context.bot.delete_message(
                chat_id=update.channel_post.chat_id,
                message_id=update.channel_post.message_id
            )
            print(f"Deleted message after 30 seconds from message ID {update.channel_post.message_id}")

# Flask route to check bot status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Bot is running!"})

def run_flask():
    # Start Flask server
    app.run(host="0.0.0.0", port=4000)

def main():
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Ensure the Flask thread exits when the main program exits
    flask_thread.start()

    # Build the bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add a handler to monitor all channel posts (messages in a channel)
    application.add_handler(MessageHandler(filters.ALL, filter_channel_posts))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
