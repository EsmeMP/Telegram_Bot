# SCRIPT PARA ENCONTRAR EL CHAT_ID DE TELEGRAM

from telegram import Update
from telegram.ext import Application, MessageHandler, filters

TOKEN = ""

async def get_chat_id(update: Update, context):
    print("CHAT ID:", update.effective_chat.id)

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, get_chat_id))

print("Send a message to your bot...")
app.run_polling()