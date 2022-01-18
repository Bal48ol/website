import telebot
import requests

TOKEN = '5016124696:AAHH8YCXjdiCWtyliXzIf73jPDmqGpI450Y'
chat_id = '-1001648151244'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Канал с рецептами: https://t.me/VsyakoeVkusnoe")


while True:
    id_key = open('telegram/lastkey.txt', 'r').read()
    for url in ['http://flask_app:5000/recept/' + id_key ]:
        try:
            response = requests.get(url)
        except Exception as http_err:
            print(f"HTTP error occurred: {http_err}")
        else:
            if response.status_code != 500:
                data = response.json()
                z = []
                for k in data.values():
                    z.append(k)
                s = ''
                for i in range(len(z)):
                    s += z[i]
                    s += "\n"
                bot.send_message(chat_id, s)
                f = open('telegram/lastkey.txt', 'w')
                f.write(str(int(id_key) + 1))
                f.close()

bot.infinity_polling()