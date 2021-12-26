import telebot
import requests
import json
import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Канал с рецептами: https://t.me/VsyakoeVkusnoe")

d = True
id = -1

while d:
    response = requests.get('http://127.0.0.1:5000/recept/<int:id>')
    data = json.loads(response)
    if id < data['id']:
        bot.send_message(config.chat_id, data['text'])
        id += 1


bot.infinity_polling()
