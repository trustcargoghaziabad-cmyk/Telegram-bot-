from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATA_FILE = "data.json"
user_state = {}

# ------------------ DATA ------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ------------------ MENUS ------------------
def main_menu():
    return ReplyKeyboardMarkup([
        ["🔍 Search Vehicle"],
        ["📊 Total Vehicles", "📤 Export Data"],
        ["📩 Send Report"],
        ["👑 Admin Panel"]
    ], resize_keyboard=True)

def admin_menu():
    return ReplyKeyboardMarkup([
        ["➕ Add Vehicle", "📥 Bulk Add"],
        ["❌ Delete Vehicle", "📋 View All"],
        ["⬅️ Back"]
    ], resize_keyboard=True)

# ------------------ START ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 *Transport Management Bot*\n\nSelect option:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ------------------ SEARCH ------------------
def search_vehicle(query):
    query = query.upper()
    results = []

    for n, o in data.items():
        if query in n:
            results.append(f"✅ {n} → {o}")

    return [f"{i+1}. {res}" for i, res in enumerate(results)]

# ------------------ HANDLER ------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # MENU ACTIONS
    if text == "🔍 Search Vehicle":
        user_state[user_id] = "search"
        return await update.message.reply_text("Enter vehicle number:")

    elif text == "📊 Total Vehicles":
        return await update.message.reply_text(f"📊 Total Vehicles: {len(data)}")

    elif text == "📤 Export Data":
        with open(DATA_FILE, "rb") as f:
            return await update.message.reply_document(f)

    elif text == "📩 Send Report":
        user_state[user_id] = "report"
        return await update.message.reply_text("Write your report:")

    elif text == "👑 Admin Panel":
        if user_id not in ADMIN_IDS:
            return await update.message.reply_text("❌ Not authorized")
        return await update.message.reply_text("Admin Panel:", reply_markup=admin_menu())

    elif text == "⬅️ Back":
        user_state[user_id] = None
        return await update.message.reply_text("Back to menu", reply_markup=main_menu())

    # ADMIN ACTIONS
    elif text == "➕ Add Vehicle":
        if user_id not in ADMIN_IDS:
            return
        user_state[user_id] = "add"
        return await update.message.reply_text("Send:\nCG1234 OWNER NAME")

    elif text == "📥 Bulk Add":
        if user_id not in ADMIN_IDS:
            return
        user_state[user_id] = "bulk"
        return await update.message.reply_text("Send multiple lines:\nCG1234 OWNER")

    elif text == "❌ Delete Vehicle":
        if user_id not in ADMIN_IDS:
            return
        user_state[user_id] = "delete"
        return await update.message.reply_text("Send vehicle number:")

    elif text == "📋 View All":
        if user_id not in ADMIN_IDS:
            return

        msg = "\n".join([f"✅ {n} → {o}" for n, o in list(data.items())[:50]])
        return await update.message.reply_text(msg if msg else "No data")

    # ---------------- STATES ----------------
    state = user_state.get(user_id)

    # SEARCH
    if state == "search":
        results = search_vehicle(text)
        if not results:
            return await update.message.reply_text("❌ No match found")
        return await update.message.reply_text("\n".join(results[:20]))

    # ADD
    elif state == "add":
        if user_id not in ADMIN_IDS:
            return

        try:
            parts = text.split()
            number = parts[0].upper()
            owner = " ".join(parts[1:])

            data[number] = owner
            save_data(data)

            return await update.message.reply_text(f"✅ Added {number}")
        except:
            return await update.message.reply_text("Format: CG1234 OWNER")

    # BULK ADD
    elif state == "bulk":
        if user_id not in ADMIN_IDS:
            return

        lines = text.split("\n")
        count = 0

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                number = parts[0].upper()
                owner = " ".join(parts[1:])
                data[number] = owner
                count += 1

        save_data(data)
        return await update.message.reply_text(f"✅ Bulk added {count} vehicles")

    # DELETE
    elif state == "delete":
        if user_id not in ADMIN_IDS:
            return

        number = text.upper()

        if number in data:
            del data[number]
            save_data(data)
            return await update.message.reply_text(f"🗑 Deleted {number}")
        else:
            return await update.message.reply_text("❌ Not found")

    # REPORT
    elif state == "report":
        report = f"📩 Report from {update.effective_user.first_name}:\n{text}"
        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=report)

        return await update.message.reply_text("✅ Report sent")

    # DEFAULT
    else:
        return await update.message.reply_text("Choose from menu", reply_markup=main_menu())

# ------------------ MAIN ------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
