import asyncio
import websockets
import json
import os.path
from datetime import datetime

PING_INTERVAL = 180  # 3 минуты в секундах
PONG_TIMEOUT = 600  # 10 минут в секундах

async def listen_to_websocket():
    websocket_url = 'wss://fstream.binance.com/ws/1000pepeusdt@bookTicker'
    
    async with websockets.connect(websocket_url) as websocket:
        try:
            print(f"{datetime.now()} | Ожидаю получения данных...")
            data = await asyncio.wait_for(websocket.recv(), timeout=60)
            print(f"{datetime.now()} | Принял сообщение: {data}")

            if 'ping' in data.lower():  # Обрабатываем пинг
                await websocket.send(data)  # Отправляем обратно тот же самый payload
                print(f"{datetime.now()} | Отправил PONG")
            else:  # Обычные данные
                # Преобразуем строку JSON в словарь
                data_dict = json.loads(data)
                print(f"{datetime.now()} | Преобразовал данные в словарь.")

                # Добавляем дату получения данных
                current_datetime = datetime.now().isoformat()
                data_dict['received_at'] = current_datetime

                # Формируем данные в нужном формате
                output_data = {
                    "type": "book_ticker_data",
                    "data": data_dict
                }

                if not os.path.exists('/home/telbot/price.json'):
                    with open('/home/telbot/price.json', 'w') as f:
                        json.dump(output_data, f, indent=4)
                    print(f"{datetime.now()} | Файл price.json создан и заполнен данными.")
                else:
                    with open('/home/telbot/price.json', 'w') as f:
                        json.dump(output_data, f, indent=4)
                    print(f"{datetime.now()} | Данные успешно обновлены в файле.")

            # Ожидание одной минуты перед следующим запросом
            print(f"{datetime.now()} | Жду 60 секунд до следующего запроса...")
            await asyncio.sleep(60)
        except asyncio.TimeoutError:
            print(f"{datetime.now()} | Истекло время ожидания данных. Повторная попытка через 120 секунд.")
            await asyncio.sleep(120)
        except Exception as e:
            print(f"{datetime.now()} | Произошла ошибка: {e}")
            print(f"{datetime.now()} | Ошибка произошла. Жду 60 секунд до следующей попытки.")
            await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(listen_to_websocket())
    except KeyboardInterrupt:
        print("\nПрерывание программы пользователем.")
    finally:
        loop.close()