from progr_command import RobotExecutor
import runpy
import socket
import time

def free_port(api):
    """
    Освобождает порт, *не отключая* питание робота:
      • корректно рвём текущий TCP-сеанс;
      • обнуляем ссылку api.socket, чтобы RobotAPI создал
        новое соединение при следующем _connect().
    """
    if api.socket:
        try:
            print("Освобождаем порт для нового подключения …")
            api.socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            api.socket.close()
        finally:
            api.socket = None  # важно для повторной инициализации

def executor(json_path, offset_table, robot_ip='localhost', speed=1.4, acceleration=0.6):
    executor = RobotExecutor(
        json_path=json_path,
        offset_table=offset_table,
        robot_ip=robot_ip,
        speed=speed,
        acceleration=acceleration
    )
    executor.run()
    print('***Алгоритм завершен***')
    free_port(executor.rr)  

if __name__ == '__main__':
    executor("titan_part11.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    runpy.run_path('loop.py', run_name='__main__')
    executor("titan_part2_1_cut.json",  {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
