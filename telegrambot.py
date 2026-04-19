from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 7365748200

# Load data
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

# Menus
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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚛 Transport Bot", reply_markup=main_menu())

# Search function
def search_vehicle(query):
    query = query.upper()
    return [f"{n} → {o}" for n, o in data.items() if query in n]

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Menu actions
    if text == "🔍 Search Vehicle":
        user_state[user_id] = "search"
        await update.message.reply_text("Enter vehicle number:")
        return

    elif text == "📊 Total Vehicles":
        await update.message.reply_text(f"Total Vehicles: {len(data)}")
        return

    elif text == "📩 Send Report":
        user_state[user_id] = "report"
        await update.message.reply_text("Write your report:")
        return

    elif text == "👑 Admin Panel":
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Not allowed")
            return
        await update.message.reply_text("Admin Panel", reply_markup=admin_menu())
        return

    elif text == "➕ Add Vehicle":
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Not allowed")
            return
        user_state[user_id] = "add"
        await update.message.reply_text("Send like:\nCG04JC4767 RAJESH ENTERPRISES")
        return

    elif text == "❌ Delete Vehicle":
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Not allowed")
            return
        user_state[user_id] = "delete"
        await update.message.reply_text("Send vehicle number:")
        return

    elif text == "⬅️ Back":
        user_state[user_id] = None
        await update.message.reply_text("Back to menu", reply_markup=main_menu())
        return

    # State-based actions
    state = user_state.get(user_id)

    if state == "search":
        results = search_vehicle(text)
        if not results:
            await update.message.reply_text("❌ No match found")
            return
        await update.message.reply_text("\n".join(results[:20]))
        return

    elif state == "add":
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ Wrong format")
            return
        data[parts[0].upper()] = " ".join(parts[1:])
        save_data(data)
        await update.message.reply_text("✅ Vehicle Added")
        return

    elif state == "delete":
        num = text.upper()
        if num in data:
            del data[num]
            save_data(data)
            await update.message.reply_text("✅ Deleted")
        else:
            await update.message.reply_text("❌ Not found")
        return

    elif state == "report":
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Report:\n{text}")
        await update.message.reply_text("✅ Report sent")
        return


# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
