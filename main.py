import telebot
import pyshorteners
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7899524124:AAGsRUGspciuweZ4VLcFdn1IpmdKqPTULp4'  # Вставь сюда свой токен
bot = telebot.TeleBot(TOKEN)

user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🖐Привет!⛓️ Отправь ссылку для сокращения.")

@bot.message_handler(func=lambda message: True)
def get_link(message):
    url = message.text.strip()
    if url.startswith("http://") or url.startswith("https://"):
        user_links[message.chat.id] = url

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🌐 TinyURL", callback_data="shorten_tinyurl"),
            InlineKeyboardButton("🧩 is.gd", callback_data="shorten_isgd"),
            InlineKeyboardButton("⚡ da.gd", callback_data="shorten_dagd")
        )
        bot.send_message(message.chat.id, "Выбери сервис для сокращения:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправь корректную ссылку (начинается с http:// или https://).")

@bot.callback_query_handler(func=lambda call: call.data.startswith("shorten_"))
def callback_shorten(call):
    service = call.data.split("_")[1]
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url:
        bot.answer_callback_query(call.id, "Ссылка не найдена. Отправь её снова.")
        return

    try:
        shortener = pyshorteners.Shortener()
        if service == "tinyurl":
            short_url = shortener.tinyurl.short(url)
        elif service == "isgd":
            short_url = shortener.isgd.short(url)
        elif service == "dagd":
            short_url = shortener.dagd.short(url)
        else:
            bot.answer_callback_query(call.id, "Неизвестный сервис.")
            return

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔗 Перейти", url=short_url),
            InlineKeyboardButton("📋 Копировать", callback_data=f"copy_{short_url}")
        )
        bot.send_message(chat_id, f"✅ Сокращено через {service}:\n{short_url}", reply_markup=markup)
        bot.answer_callback_query(call.id, "Готово!")

    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка при сокращении. Попробуй другой сервис.")
        bot.answer_callback_query(call.id, "Ошибка.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def copy_link(call):
    short_url = call.data.replace("copy_", "")
    bot.send_message(call.message.chat.id, f"📋 Скопируй ссылку:\n{short_url}")
    bot.answer_callback_query(call.id, "Ссылка скопирована 👍 (ну почти)")

bot.polling()