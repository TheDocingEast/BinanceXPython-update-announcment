import requests
from gigachat import GigaChat
import time 
import requests
import telebot
import os
# Отключение проверки сертификатов (не рекомендуется в продакшене!)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Замените 'ваш_токен' на ваш реальный токен доступа
credentials = 'YjJmOTJkN2QtMDI1Zi00ZGQxLTkxNzAtNjViZTg2MmZkM2VmOjg3NDdkMjY2LTZiY2EtNDFkMC1iYmE2LThlYWI0YmQ0Nzk5Ng=='
bot = telebot.TeleBot('6493912171:AAHKpltnLc7j8hvEMKHKHFwlRam3cB591Yw')
# Создаем экземпляр класса GigaChat
model = GigaChat(credentials=credentials, model="GigaChat", verify_ssl_certs=False)


@bot.message_handler(commands=['start'])
def send_start(message):
        bot.reply_to(message, 'Привет, я бот для работы с GigaChat от Sber, после этого сообщения вводи свой запрос и ты получишь ответ от нейросети.')

@bot.message_handler(func=lambda message: True)
def answer(message):
    user_input = message.text
        
    if not user_input:
        pass
        
    try:
        response = model.chat(user_input)
        answer = response.choices[0].message.content
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    
def main():
    start_time = time.time()
    elapsed_time = start_time - time.time()
        
    if elapsed_time > 1800:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload={
        'scope': 'GIGACHAT_API_PERS'
        }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': 'c11a0542-c022-4380-845f-15f23ada1d07',
        'Authorization': 'Basic <Authorization key>'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
            
if __name__ == "__main__":
    bot.polling()
    main()