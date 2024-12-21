"""
Перед вами прокси-сервер на python, использующий только средства стандартной библиотеки Python.
Данная реализация подерживает только http-протокол и не работает с его расширением, https.
Запуск:
    Для Windows:
        Введите в консоли (например, Powershell) команду
            ```python proxy_server_00.py```
        В другой консоли введите
            ```Invoke-WebRequest -Proxy "http://127.0.0.1:8888" -Uri "http://httpbin.org/ip"```
    Для Linux:
        Введите в консоли команду
            ```python3 proxy_server_00.py```
        В другой консоли введите
            ```curl --proxy "http://127.0.0.1:8888" "http://httpbin.org/ip"```
В примере ниже используется print для вывода результат в консоль. В "боевой" разработке рекомендуется запускать код в
режиме DEBUG для отладки кода и получения значения перменных "на лету", а при запуске кода на сервере - библиотеку
logging для сбора отладочной информации.
"""

import socket
import threading


def handle_client_request(client_socket):
    """Функция для обработки входящих запросов"""
    print("Полученный запрос:\n")
    # Читаем данные, отправленные клиентом в запросе
    request = b''
    client_socket.setblocking(False)
    while True:
        try:
            # Получаем данные с веб-сервера
            data = client_socket.recv(1024)
            request = request + data
            print(f"{data.decode('utf-8')}")
        except:
            break
    # Извлекаем хост и порт целевого веб-сервера из запроса
    host, port = extract_host_port_from_request(request)
    # Создаём сокет для подключения к целевому серверу
    destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Подключаемся к целевому серверу
    destination_socket.connect((host, port))
    # Отправляем исходный запрос в нужное место назначения
    destination_socket.sendall(request)
    print("Полученный ответ:\n")
    while True:
        # Получаем данные с целевого веб-сервера
        data = destination_socket.recv(1024)
        print(f"{data.decode('utf-8')}")
        # Если данные не пусты, отправляем их клиенту, иначе прерываем операцию
        if len(data) > 0:
            client_socket.sendall(data)
        else:
            break
    destination_socket.close()
    client_socket.close()


def extract_host_port_from_request(request):
    """Функция для извлечения хоста и порта из запроса.
       Если порт не указан, то используем значение "80" - по умолчанию для http-соединения"""
    host_string_start = request.find(b'Host: ') + len(b'Host: ')
    host_string_end = request.find(b'\r\n', host_string_start)
    host_string = request[host_string_start:host_string_end].decode('utf-8')
    webserver_pos = host_string.find("/")

    if webserver_pos == -1:
        webserver_pos = len(host_string)
    port_pos = host_string.find(":")
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        host = host_string[:webserver_pos]
    else:
        port = int((host_string[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        host = host_string[:port_pos]
    return host, port


def start_proxy_server():
    """Функция для запуска прокси-сервера"""
    port = 8888
    # Связываем прокси-сервер с локальным адресом - http://127.0.0.1:8888
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    # Принимаем до 10 одновременных подключений
    server.listen(10)
    print(f"Прокси-сервер слушает порт {port}...")
    # Слушаем входящие запросы
    while True:
        # Создаём клиентский сокет
        client_socket, addr = server.accept()
        print(f"Принято соединение от {addr[0]}:{addr[1]}")
        # Создаём поток для одновременной обработки нескольких клиентских запросов
        client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_proxy_server()
