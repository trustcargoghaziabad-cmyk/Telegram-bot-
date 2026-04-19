from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json

# 🔑 आपका Bot Token
TOKEN = "YOUR_BOT_TOKEN_HERE"

# 👑 Admin ID (अपना Telegram ID डालो)
ADMIN_ID = 7365748200

# =========================
# 📂 DATA LOAD / SAVE
# =========================
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

# =========================
# 📋 MENUS
# =========================
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

# =========================
# 🚀 START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 *Transport Management Bot*\n\nChoose an option below:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# =========================
# 🔍 SEARCH FUNCTION
# =========================
def search_vehicle(query):
    query = query.upper()
    return [f"{n} → {o}" for n, o in data.items() if query in n]

# =========================
# 💬 HANDLE MESSAGES
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # ===== MENU ACTIONS =====
    if text == "🔍 Search Vehicle":
        user_state[user_id] = "search"
        return await update.message.reply_text("Enter vehicle number:")

    elif text == "📊 Total Vehicles":
        return await update.message.reply_text(f"📊 Total Vehicles: {len(data)}")

    elif text == "📩 Send Report":
        user_state[user_id] = "report"
        return await update.message.reply_text("✍️ Write your report:")

    elif text == "👑 Admin Panel":
        if user_id != ADMIN_ID:
            return await update.message.reply_text("❌ Access Denied")
        return await update.message.reply_text("👑 Admin Panel", reply_markup=admin_menu())

    elif text == "➕ Add Vehicle":
        if user_id != ADMIN_ID:
            return
        user_state[user_id] = "add"
        return await update.message.reply_text("Send like:\nCG04XX1234 Owner Name")

    elif text == "❌ Delete Vehicle":
        if user_id != ADMIN_ID:
            return
        user_state[user_id] = "delete"
        return await update.message.reply_text("Send vehicle number to delete")

    elif text == "⬅️ Back":
        return await update.message.reply_text("⬅️ Back to Menu", reply_markup=main_menu())

    # ===== STATE HANDLING =====
    state = user_state.get(user_id)

    # 🔍 SEARCH
    if state == "search":
        results = search_vehicle(text)
        if not results:
            return await update.message.reply_text("❌ No match found")

        reply = "\n".join(results[:20])
        if len(results) > 20:
            reply += f"\n\n...and {len(results)-20} more"

        return await update.message.reply_text(reply)

    # ➕ ADD VEHICLE
    elif state == "add" and user_id == ADMIN_ID:
        parts = text.split()
        if len(parts) < 2:
            return await update.message.reply_text("❌ Invalid format")

        vehicle = parts[0].upper()
        owner = " ".join(parts[1:])

        data[vehicle] = owner
        save_data(data)

        return await update.message.reply_text("✅ Vehicle Added")

    # ❌ DELETE VEHICLE
    elif state == "delete" and user_id == ADMIN_ID:
        vehicle = text.upper()

        if vehicle in data:
            del data[vehicle]
            save_data(data)
            return await update.message.reply_text("✅ Vehicle Deleted")
        else:
            return await update.message.reply_text("❌ Not Found")

    # 📩 REPORT SYSTEM
    elif state == "report":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 *New Report:*\n\n{text}",
            parse_mode="Markdown"
        )
        return await update.message.reply_text("✅ Report sent")

# =========================
# 🏁 MAIN
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
