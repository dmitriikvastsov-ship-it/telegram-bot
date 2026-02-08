from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("8206002890:AAEbMQE18YPiduFjhfeW2p4X_omV8uAbWd4")
ADMIN_ID = [544424687, 637280953]

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"step": 1}

    keyboard = [["Да", "Нет"]]

    await update.message.reply_text(
        "Здравствуйте!\n\n"
        "1. Есть ли у вас бумажные международные водительские права (МВУ)?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users:
        return

    step = users[user_id]["step"]

    if step == 1:
        if text.lower() == "нет":
            await update.message.reply_text(
                "К сожалению, без МВУ аренда невозможна.",
                reply_markup=ReplyKeyboardRemove()
            )
            del users[user_id]
            return

        users[user_id]["mvu"] = text
        users[user_id]["step"] = 2

        keyboard = [["4", "5"], ["7+"]]
        await update.message.reply_text(
            "2. Сколько мест нужно?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    if step == 2:
        users[user_id]["seats"] = text
        users[user_id]["step"] = 3

        keyboard = [["Автомат", "Механика"], ["Неважно"]]
        await update.message.reply_text(
            "3. Какая коробка передач?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    if step == 3:
        users[user_id]["gear"] = text
        users[user_id]["step"] = 4
        await update.message.reply_text(
            "4. Напишите даты аренды",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if step == 4:
        users[user_id]["dates"] = text
        users[user_id]["step"] = 5
        await update.message.reply_text("5. Город начала аренды")
        return

    if step == 5:
        users[user_id]["city"] = text
        users[user_id]["step"] = 6
        await update.message.reply_text("6. Самая дальняя точка маршрута")
        return

    if step == 6:
        users[user_id]["route"] = text

        user = update.effective_user

        message = (
            f"Новая заявка\n\n"
            f"Имя: {user.first_name}\n"
            f"Username: @{user.username}\n\n"
            f"МВУ: {users[user_id]['mvu']}\n"
            f"Мест: {users[user_id]['seats']}\n"
            f"Коробка: {users[user_id]['gear']}\n"
            f"Даты: {users[user_id]['dates']}\n"
            f"Город: {users[user_id]['city']}\n"
            f"Маршрут: {users[user_id]['route']}"
        )

        for admin in ADMIN_ID:
            await context.bot.send_message(admin, message)

        await update.message.reply_text("Спасибо! Заявка отправлена.")
        del users[user_id]


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
