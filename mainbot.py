import os
import schedule
from selenium.webdriver.common.by import By
import selenium.webdriver
import json
from gigachat import GigaChat
import telebot
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from dotenv import load_dotenv
load_dotenv()
# Настройки
BASE_URL = 'https://www.binance.com/en/support/announcement/api-updates?c=51&navId=51'
TITLE_CLASS_NAME = 'div.gap-4:nth-child(1) > div:nth-child(1) > a:nth-child(1) > h3:nth-child(1)'
URL_NAME = 'div.gap-4:nth-child(1) > div:nth-child(1) > a:nth-child(1)'
SAVE_FILES = '/home/telbot/data.json'     # Директория для сохранения изображений
credentials = os.getenv("GIGACHAT_API")
bot = telebot.TeleBot(os.getenv("TELEGRAM_API"))
# Создаем экземпляр класса GigaChat
model = GigaChat(credentials=credentials, model="GigaChat", verify_ssl_certs=False)
options = selenium.webdriver.FirefoxOptions()
options.add_argument('--headless')  # Запуск в фоновом режиме (без GUI)
# Создаем основную директорию для сохранения изображений
if not os.path.exists(SAVE_FILES):
    with open(SAVE_FILES, 'w') as f:
            json.dump({}, f)

# Настройка драйвера Firefox
keyboard = telebot.types.InlineKeyboardMarkup()
button1 = telebot.types.InlineKeyboardButton('Последнее обновление', callback_data='callback_1')
button2 = telebot.types.InlineKeyboardButton('Сайт с обновлениями', url='https://www.binance.com/en/support/announcement/api-updates?c=51&navId=51')
button3 = telebot.types.InlineKeyboardButton('Цена PEPE', callback_data='callback_2')
keyboard.add(button1, button2, button3)
        
@bot.message_handler(commands=['start'])
def send_start(message):
        bot.send_message(message.chat.id, 'Привет, я бот для работы с Binance, я могу отправлять оповещения об обновлениях в API, или активности на рынке.', reply_markup=keyboard)
        
def write_to_json(SAVE_FILES, data):
    with open(SAVE_FILES, 'r+') as file:
        # Читаем содержимое файла
        file_content = json.load(file)
        
        # Объединяем новые данные с существующими
        file_content.update(data)
        
        # Перемещаемся в начало файла
        file.seek(0)
        
        # Перезаписываем файл новыми данными
        json.dump(file_content, file, indent=4)
        
        # Чистим буфер и закрываем файл
        file.truncate()
        
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'callback_1':
        try:

            driver = selenium.webdriver.Firefox(options=options)
            driver.get(BASE_URL)
            # Находим все элементы с нужным классом для изображений и названий
            title_class = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, TITLE_CLASS_NAME)))
            url_class = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, URL_NAME)))
            titles = [title.text for title in title_class]
            urls = [url_classes.get_attribute('href') for url_classes in url_class]
            data = {'titles': titles,
            'urls': urls}
            print(data)
            driver.quit()
            with open(SAVE_FILES, 'r+') as file:
                # Читаем содержимое файла
                file_content = json.load(file)
                # Объединяем новые данные с существующими
                file_content.update(data)
                # Перемещаемся в начало файла
                file.seek(0)
                # Перезаписываем файл новыми данными
                json.dump(file_content, file, indent=4)
                # Чистим буфер и закрываем файл
                file.truncate()
            for title, url in zip(data["titles"], data["urls"]):
                bot.send_message(call.message.chat.id, f"Последнее вышедшее обновление: <a href='{url}'>{title}</a>", parse_mode="HTML", reply_markup=keyboard)
                
        except Exception as e:
            bot.send_message(call.message.chat.id, f'Не удалось получить данные сайта, ошибка {e}, отправьте ошибку по адресу: .....', reply_markup=keyboard)
    elif call.data == 'callback_2':
        print('Отправка цены PEPE1000')
        with open('/home/telbot/price.json', 'r+') as f:
            data = json.load(f)
            book_ticker_data = data['data']
            message = format_telegram_message(book_ticker_data)
            print(message)
        response = model.chat(f'''Вот информация о цене PEPE1000USDT через, расшифруй её по информации из Websocket Market Streams API Binance. Сгенерируй краткую справку о ситуации на рынке, сами данные:{data}. НЕ ИСПОЛЬЗУЙ ** в сообщении. Вот пример как писать, в конце пиши свои рекомендации:
                                "📊 Название валюты 📊\n\n"
                                Лучшая цена покупки: , ( токенов (количество))\n"
                                Лучшая цена продажи: , ( токенов (количество))\n"
                                Время получения данных:  UTC (из файла)"''')
        answer = response.choices[0].message.content
        
        bot.send_message(call.message.chat.id, answer, reply_markup=keyboard)
                

def format_telegram_message(book_ticker_data):
    received_at = book_ticker_data["received_at"]
    best_bid_price = book_ticker_data["b"]
    bid_name = book_ticker_data["s"]
    best_bid_quantity = book_ticker_data["B"]
    best_ask_price = book_ticker_data["a"]
    best_ask_quantity = book_ticker_data["A"]
    formatted_time = datetime.fromisoformat(received_at).strftime('%Y-%m-%d %H:%M:%S')
    
    message = (
        f"📊 Цена {bid_name} 📊\n\n"
        f"Лучшая цена покупки: {best_bid_price} ({best_bid_quantity} токенов)\n"
        f"Лучшая цена продажи: {best_ask_price} ({best_ask_quantity} токенов)\n"
        f"\nВремя получения данных: {formatted_time} UTC"
    )
    
    return message

def main():
    start_time = datetime.now()
    elapsed_time = start_time - datetime.now()
        
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

def check_data(message):
    driver = selenium.webdriver.Firefox(options=options)
    driver.get(BASE_URL)
    # Находим все элементы с нужным классом для изображений и названий
    title_class = driver.find_elements(By.CSS_SELECTOR, TITLE_CLASS_NAME)
    url_class = driver.find_elements(By.CSS_SELECTOR, URL_NAME)
    titles = [title.text for title in title_class]
    urls = [url_classes.get_attribute('href') for url_classes in url_class]
    data = {'titles': titles,
                    'urls': urls}
    print(data)
    for old_title, old_url in zip(data["titles"], data["urls"]):
        if old_title != titles and old_url !=urls:
            data = {'titles': titles,
                    'urls': urls}
            print(f'Новые данные: {data}')
            bot.send_message(message.chat.id, f"Вышло новое обновление: <a href='{urls}'>{titles}</a>", parse_mode="HTML", reply_markup=keyboard)
    driver.quit()
    with open(SAVE_FILES, 'r+') as file:
        # Читаем содержимое файла
        file_content = json.load(file)
        # Объединяем новые данные с существующими
        file_content.update(data)
        # Перемещаемся в начало файла
        file.seek(0)
        # Перезаписываем файл новыми данными
        json.dump(file_content, file, indent=4)
        # Чистим буфер и закрываем файл
        file.truncate()
                



schedule.every().day.at("00:00").do(check_data)
if __name__ == "__main__":
    bot.polling()
    main()
    schedule.run_pending()
    