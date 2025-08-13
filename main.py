import os
import telebot
import openai

# Настройки из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

chat_history = {}

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Этот бот личный. Доступ запрещён.")
        return

    user_id = message.from_user.id
    chat_history.setdefault(user_id, [])
    chat_history[user_id].append({"role": "user", "content": message.text})

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=chat_history[user_id]
    )

    reply = completion.choices[0].message["content"]
    chat_history[user_id].append({"role": "assistant", "content": reply})
    bot.reply_to(message, reply)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Этот бот личный. Доступ запрещён.")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Опиши это изображение и сделай выводы."},
                    {"type": "image_url", "image_url": file_url}
                ]
            }
        ]
    )

    bot.reply_to(message, completion.choices[0].message["content"])

if __name__ == "__main__":
    bot.polling()
