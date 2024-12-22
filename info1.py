from flask import Flask, jsonify
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests

# Flask app setup
app = Flask(__name__)

# Main group IDs and Admin IDs
MAIN_GROUP_IDS = [-1002407057073,-1002404360776]
MAIN_ADMIN_IDS = [7318766583, 6135934591, 6095233308]

# Updated Temporary groups and admins
TEMPORARY_GROUPS = [-1002407057073, -1002378058101, -1002165957353, -1002496835107]  # New temporary groups
TEMPORARY_ADMINS = [6547214889, 7314227803]  # New temporary admins

# Dictionary to manage allowed groups and temporary admins
allowed_group_ids = {}
temporary_admins = {}

# Function to fetch player data from API
def get_player_info(region, uid):
    if not uid.isdigit() or not (8 <= len(uid) <= 11):
        return {"error": "Invalid UID"}
    url = f"https://www.info.freefireinfo.site/api/{region}/{uid}?key=nishant881891"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": f"API Error: {response.status_code}, {response.text}"}
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to automatically grant permission
def grant_automatic_permission(chat_id, user_id):
    # If the group is in the temporary groups list, give automatic permission for 99 days
    if chat_id in TEMPORARY_GROUPS:
        allowed_group_ids[chat_id] = datetime.now() + timedelta(days=69)
    
    # If the user is in the temporary admins list, grant temporary admin access for 99 days
    if user_id in TEMPORARY_ADMINS:
        temporary_admins[user_id] = datetime.now() + timedelta(days=69)

# Command: /allow
async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id in MAIN_ADMIN_IDS or user_id in temporary_admins:
        try:
            days = int(context.args[0])
            allowed_group_ids[chat_id] = datetime.now() + timedelta(days=days)
            await update.message.reply_text(f"🥰Group allowed for {days} days❤.")
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /allow <days>")
    else:
        await update.message.reply_text("🙃You do not have permission to use this command.\n💸 Buy access from  @MUKESHSARKAR69 ✔️")

# Command: /remove
async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id in MAIN_ADMIN_IDS:
        if chat_id in allowed_group_ids:
            del allowed_group_ids[chat_id]
            await update.message.reply_text("💔Group removed from the allowed list💔.")
        else:
            await update.message.reply_text("💔This group is not in the allowed list💔.\nUse VIP group https://t.me/freefirelikesvip || BUY ACCESS FROM ☠️ @Nishantsarkar10k ✔️")
    else:
        await update.message.reply_text("😂You do not have permission to use this command😂.\nBuy access from ☠️ @MUKESHSARKAR69 ✔️")

# Command: /addadmin
async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in MAIN_ADMIN_IDS:
        try:
            days = int(context.args[0])
            target_user_id = update.message.reply_to_message.from_user.id
            temporary_admins[target_user_id] = datetime.now() + timedelta(days=days)
            await update.message.reply_text(f"User {target_user_id} is now a temporary admin for {days} days❤.")
        except (IndexError, ValueError, AttributeError):
            await update.message.reply_text("Usage: Reply to a user with /addadmin <days>")
    else:
        await update.message.reply_text("🙃You do not have permission to use this command🙃.\nBuy access from ☠️ @MUKESHSARKAR69 ✔️")

# Command: /removeadmin
async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in MAIN_ADMIN_IDS:
        try:
            target_user_id = update.message.reply_to_message.from_user.id
            if target_user_id in temporary_admins:
                del temporary_admins[target_user_id]
                await update.message.reply_text(f"💔User {target_user_id} is no longer a temporary admin💔.")
            else:
                await update.message.reply_text("💔This user is not a temporary admin💔.")
        except AttributeError:
            await update.message.reply_text("Reply to a user with /removeadmin to remove their admin status.")
    else:
        await update.message.reply_text("🙃You do not have permission to use this command,🙃.\nBuy access from @MUKESHSARKAR69 ✔️")

# Command: /me
async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in temporary_admins:
        remaining_time = temporary_admins[user_id] - datetime.now()
        days, seconds = remaining_time.days, remaining_time.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        await update.message.reply_text(f"Your temporary admin status will expire 💔 in {days} days, {hours} hours, and {minutes} minutes.")
    else:
        await update.message.reply_text("💔You are not a temporary admin💔.\n💸 Buy access from ☠️ @MUKESHSARKAR69 ✔️")

# Command: /get
async def get_player_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in MAIN_GROUP_IDS and chat_id not in allowed_group_ids:
        await update.message.reply_text("💔This group is not allowed to use the bot💔.\nContact @Nishantsarkar10k to buy permission || /nUse VIP group https://t.me/freefirelikesvip ✔️")
        return

    try:
        region, uid = context.args[0], context.args[1]
        player_data = get_player_info(region, uid)
        if "error" in player_data:
            await update.message.reply_text("Error fetching player data. Ensure the command is formatted as: /get <region> <uid>")
            return
        await update.message.reply_text(format_player_data(player_data))
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /get <region> <uid>")

# Format player data into the required structure
def format_player_data(player_data):
    basic_info = player_data.get("basicInfo", {})
    pet_info = player_data.get("petInfo", {})
    profile_info = player_data.get("profileInfo", {})
    clan_info = player_data.get("clanBasicInfo", {})
    captain_info = player_data.get("captainBasicInfo", {})
    social_info = player_data.get("socialInfo", {})
    credit_score = player_data.get("creditScoreInfo", {}).get("creditScore", "N/A")

    created_at = datetime.fromtimestamp(int(basic_info.get("createAt", 0))).strftime('%d %B %Y at %H:%M:%S') if "createAt" in basic_info else "N/A"
    last_login = datetime.fromtimestamp(int(basic_info.get("lastLoginAt", 0))).strftime('%d %B %Y at %H:%M:%S') if "lastLoginAt" in basic_info else "N/A"

    leader_created_at = datetime.fromtimestamp(int(captain_info.get("createAt", 0))).strftime('%d %B %Y at %H:%M:%S') if "createAt" in captain_info else "N/A"
    leader_last_login = datetime.fromtimestamp(int(captain_info.get("lastLoginAt", 0))).strftime('%d %B %Y at %H:%M:%S') if "lastLoginAt" in captain_info else "N/A"
    leader_title = captain_info.get("title", "N/A")
    leader_bp_badges = captain_info.get("badgeCnt", "N/A")
    leader_br_points = captain_info.get("rankingPoints", "N/A")
    leader_cs_points = captain_info.get("csRankingPoints", "N/A")
    return (
        f"ACCOUNT INFO:\n"
        f"┌ 👤 ACCOUNT BASIC INFO\n"
        f"├─ Name: {basic_info.get('nickname', 'N/A')}\n"
        f"├─ UID: {basic_info.get('accountId', 'N/A')}\n"
        f"├─ Level: {basic_info.get('level', 'N/A')} (Exp: {basic_info.get('exp', 'N/A')})\n"
        f"├─ Region: {basic_info.get('region', 'N/A')}\n"
        f"├─ Likes: {basic_info.get('liked', 'N/A')}\n"
        f"├─ Honor Score: {credit_score}\n"
        f"├─ Celebrity Status: {'True' if profile_info.get('isMarkedStar') else 'False'}\n"
        f"├─ Evo Access Badge: {basic_info.get('badgeId', 'Inactive')}\n"
        f"├─ Title: {basic_info.get('title', 'N/A')}\n"
        f"├─ Signature: {social_info.get('signature', 'N/A')}\n"
        f"└─ Outfits: Graphically Presented Below! 😉\n\n"
        f"┌ 🎮 ACCOUNT ACTIVITY\n"
        f"├─ Most Recent OB: {basic_info.get('releaseVersion', 'N/A')}\n"
        f"├─ Fire Pass: {'Premium' if basic_info.get('badgeCnt') else 'Free'}\n"
        f"├─ Current BP Badges: {basic_info.get('badgeCnt', 'N/A')}\n"
        f"├─ BR Rank: {basic_info.get('rank', 'N/A')} ({basic_info.get('rankingPoints', 'N/A')})\n"
        f"├─ CS Points: {basic_info.get('csRank', 'N/A')}\n"
        f"├─ Created At: {created_at}\n"
        f"└─ Last Login: {last_login}\n\n"
        f"┌ 👕 ACCOUNT OVERVIEW\n"
        f"├─ Avatar ID: {profile_info.get('avatarId', 'N/A')}\n"
        f"├─ Banner ID: {basic_info.get('badgeId', 'N/A')}\n"
        f"├─ Pin ID: {basic_info.get('pinId', 'N/A')}\n"
        f"├─ Equipped Skills: {', '.join([str(skill.get('skillId', 'N/A')) for skill in profile_info.get('equipedSkills', [])])}\n"
        f"└─ Outfits: Graphically Presented Below! 😉\n\n"
        f"┌ 🐾 PET DETAILS\n"
        f"├─ Equipped?: {'Yes' if pet_info.get('isSelected') else 'No'}\n"
        f"├─ Pet Name: {pet_info.get('name', 'N/A')}\n"
        f"├─ Pet Type: {pet_info.get('id', 'N/A')}\n"
        f"├─ Pet Exp: {pet_info.get('exp', 'N/A')}\n"
        f"└─ Pet Level: {pet_info.get('level', 'N/A')}\n\n"
        f"┌ 🛡️ GUILD INFO\n"
        f"├─ Guild Name: {clan_info.get('clanName', 'N/A')}\n"
        f"├─ Guild ID: {clan_info.get('clanId', 'N/A')}\n"
        f"├─ Guild Level: {clan_info.get('clanLevel', 'N/A')}\n"
        f"├─ Live Members: {clan_info.get('memberNum', 'N/A')}\n"
        f"└─ Leader Info:\n"
        f"    ├─ Leader Name: {captain_info.get('nickname', 'N/A')}\n"
        f"    ├─ Leader UID: {captain_info.get('accountId', 'N/A')}\n"
        f"    ├─ Leader Level: {captain_info.get('level', 'N/A')} (Exp: {captain_info.get('exp', 'N/A')})\n"
        f"    ├─ Leader BR Points: {leader_br_points}\n"
        f"    ├─ Leader CS Points: {leader_cs_points}\n"
        f"    ├─ Leader Title: {leader_title}\n"
        f"    ├─ Leader Current BP Badges: {leader_bp_badges}\n"
        f"    ├─ Leader Created At: {leader_created_at}\n"
        f"    └─ Leader Last Login: {leader_last_login}\n"
        f"OWNER - ☠️ @MUKESHSARKAR69 ✔️\n\n"
        f"💙FF LIKES GROUP - https://t.me/mukeshsarkar01 ❤\n" 
    )

# Flask endpoint to check bot status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Bot is online"}), 200

# Flask endpoint to fetch player information
@app.route('/get/<region>/<uid>', methods=['GET'])
def get_player(region, uid):
    player_data = get_player_info(region, uid)
    if "error" in player_data:
        return jsonify({"error": player_data["error"]}), 400
    return jsonify({"message": format_player_data(player_data)}), 200

# Main function to run Flask and Telegram bot
if __name__ == '__main__':
    from threading import Thread
    from telegram.ext import ApplicationBuilder

    # Start Flask in a separate thread
    def run_flask():
        app.run(host="0.0.0.0", port=7080)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Initialize Telegram bot
    application = ApplicationBuilder().token("7198659869:AAFzr50cWltTZSoDfIt_JozzTx8Bk0GRIZ0").build()

    # Ensure that temporary admins and groups are granted access on startup
    for group_id in TEMPORARY_GROUPS:
        allowed_group_ids[group_id] = datetime.now() + timedelta(days=99)
    
    for admin_id in TEMPORARY_ADMINS:
        temporary_admins[admin_id] = datetime.now() + timedelta(days=99)

    application.add_handler(CommandHandler("allow", allow_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("me", me_command))
    application.add_handler(CommandHandler("get", get_player_command))

    application.run_polling()
