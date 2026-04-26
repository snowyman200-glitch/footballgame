import os
import json
from dotenv import load_dotenv
import httpx
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
WEB_APP_URL = os.getenv('WEB_APP_URL', '')
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', '')

if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN is missing')
if not WEB_APP_URL:
    raise RuntimeError('WEB_APP_URL is missing')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton(text='Открыть игру', web_app=WebAppInfo(url=WEB_APP_URL))
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text(
        'Привет. Для старта нажми ИГРАТЬ.',
        reply_markup=markup,
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Mini App: {WEB_APP_URL}\nAPI: {BACKEND_BASE_URL or "не задан"}')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/start — открыть игру\n/status — статус подключений')

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.web_app_data:
        return
    try:
        payload = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text('Не удалось прочитать JSON из Mini App')
        return
    await update.message.reply_text('Данные из Mini App получены ✅')
    if BACKEND_BASE_URL:
        user = update.effective_user
        body = {
            'tournament_slug': payload.get('tournament_slug', 'world-cup-2026-demo'),
            'user': {
                'telegram_user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language_code': user.language_code,
            },
            'bracket_payload': payload,
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(f'{BACKEND_BASE_URL}/api/submissions', json=body)
                r.raise_for_status()
            await update.message.reply_text('Прогноз сохранён на сервере')
        except Exception:
            await update.message.reply_text('API недоступен, но Telegram получил данные')


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    app.run_polling()

if __name__ == '__main__':
    main()
