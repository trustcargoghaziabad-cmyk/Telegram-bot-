from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import json
import os

# ENV VARIABLES
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Load Data
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
user_state = {}

# MENUS
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔍 Search Vehicle")],
        [KeyboardButton("📊 Total Vehicles"), KeyboardButton("📩 Send Report")],
        [KeyboardButton("👑 Admin Panel")]
    ], resize_keyboard=True)

def admin_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Add Vehicle"), KeyboardButton("❌ Delete Vehicle")],
        [KeyboardButton("⬅️ Back")]
    ], resize_keyboard=True)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚛 Transport Bot Started", reply_markup=main_menu())

# SEARCH
def search_vehicle(query):
    query = query.upper()
    return [f"{n} → {o}" for n, o in data.items() if query in n]

# HANDLE MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # MENU
    if text == "🔍 Search Vehicle":
        user_state[user_id] = "search"
        return await update.message.reply_text("Enter vehicle number:")

    elif text == "📊 Total Vehicles":
        return await update.message.reply_text(f"Total Vehicles: {len(data)}")

    elif text == "📩 Send Report":
        user_state[user_id] = "report"
        return await update.message.reply_text("Write your report:")

    elif text == "👑 Admin Panel":
        if user_id != ADMIN_ID:
            return await update.message.reply_text("❌ Not allowed")
        return await update.message.reply_text("Admin Panel", reply_markup=admin_menu())

    elif text == "➕ Add Vehicle":
        if user_id != ADMIN_ID:
            return
        user_state[user_id] = "add"
        return await update.message.reply_text("Send like:\nCG04XX1234 OWNER NAME")

    elif text == "❌ Delete Vehicle":
        if user_id != ADMIN_ID:
            return
        user_state[user_id] = "delete"
        return await update.message.reply_text("Send vehicle number to delete:")

    elif text == "⬅️ Back":
        user_state[user_id] = None
        return await update.message.reply_text("Back", reply_markup=main_menu())

    # STATES
    state = user_state.get(user_id)

    if state == "search":
        results = search_vehicle(text)
        if not results:
            return await update.message.reply_text("❌ No match found")
        return await update.message.reply_text("\n".join(results[:20]))

    elif state == "add" and user_id == ADMIN_ID:
        parts = text.split()
        if len(parts) < 2:
            return await update.message.reply_text("❌ Format wrong")

        vehicle = parts[0].upper()
        owner = " ".join(parts[1:])

        data[vehicle] = owner
        save_data(data)

        return await update.message.reply_text("✅ Vehicle Added")

    elif state == "delete" and user_id == ADMIN_ID:
        vehicle = text.upper()

        if vehicle in data:
            del data[vehicle]
            save_data(data)
            return await update.message.reply_text("✅ Deleted")

        return await update.message.reply_text("❌ Not found")

    elif state == "report":
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Report:\n{text}")
        return await update.message.reply_text("✅ Report sent")

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # FIXED LINE (IMPORTANT)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
