from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json

TOKEN = "8452914839:AAETzJqHle8oQrZgwcOHvvNCQzWJ9m7KJmE"
ADMIN_ID = 7365748200 # your Telegram ID

# ------------------ DATA ------------------
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

# ------------------ MENU ------------------
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

# ------------------ START ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 Transport Management Bot\n\nChoose an option:",
        reply_markup=main_menu()
    )

# ------------------ SEARCH ------------------
def search_vehicle(query):
    query = query.upper()
    results = [f"✅ {n} → {o}" for n, o in data.items() if query in n]
    return [f"{i+1}. {res}" for i, res in enumerate(results)]

# ------------------ MESSAGE HANDLER ------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # 🔍 Search Button
    if text == "🔍 Search Vehicle":
        user_state[user_id] = "search"
        return await update.message.reply_text("Enter vehicle number:")

    # 📊 Total
    elif text == "📊 Total Vehicles":
        return await update.message.reply_text(f"📊 Total: {len(data)} vehicles")

    # 📩 Report
    elif text == "📩 Send Report":
        user_state[user_id] = "report"
        return await update.message.reply_text("Write your issue/report:")

    # 👑 Admin Panel
    elif text == "👑 Admin Panel":
        if user_id != ADMIN_ID:
            return await update.message.reply_text("❌ Not authorized")
        return await update.message.reply_text("Admin Panel:", reply_markup=admin_menu())

    # ➕ Add
    elif text == "➕ Add Vehicle":
        user_state[user_id] = "add"
        return await update.message.reply_text("Send: VEHICLE OWNER")

    # ❌ Delete
    elif text == "❌ Delete Vehicle":
        user_state[user_id] = "delete"
        return await update.message.reply_text("Send vehicle number to delete:")

    # ⬅️ Back
    elif text == "⬅️ Back":
        return await update.message.reply_text("Back to menu", reply_markup=main_menu())

    # ------------------ STATES ------------------

    state = user_state.get(user_id)

    # SEARCH
    if state == "search":
        results = search_vehicle(text)
        if not results:
            return await update.message.reply_text("❌ No match found")
        return await update.message.reply_text("\n".join(results[:20]))

    # ADD (ADMIN)
    elif state == "add":
        if user_id != ADMIN_ID:
            return await update.message.reply_text("❌ Not authorized")

        try:
            parts = text.split()
            number = parts[0].upper()
            owner = " ".join(parts[1:])
            data[number] = owner
            save_data(data)
            return await update.message.reply_text(f"✅ Added {number}")
        except:
            return await update.message.reply_text("Format: CG1234 NAME")

    # DELETE (ADMIN)
    elif state == "delete":
        if user_id != ADMIN_ID:
            return await update.message.reply_text("❌ Not authorized")

        number = text.upper()
        if number in data:
            del data[number]
            save_data(data)
            return await update.message.reply_text(f"🗑 Deleted {number}")
        else:
            return await update.message.reply_text("❌ Not found")

    # REPORT
    elif state == "report":
        report_msg = f"📩 REPORT from {update.effective_user.first_name}:\n{text}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=report_msg)
        return await update.message.reply_text("✅ Report sent to admin")

    # DEFAULT
    else:
        await update.message.reply_text("Please select option from menu", reply_markup=main_menu())

# ------------------ MAIN ------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Professional Transport Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
