from progr_command import RobotExecutor
import runpy
import socket
import time

# import loop

def free_port(api) -> None:
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

# if __name__ == '__main__':
#     executor1 = RobotExecutor(
#         json_path="titan_part11.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor1.run()
#     free_port(executor1.rr)

# # runpy.run_path('loop.py', run_name='__main__')

# # if __name__ == '__main__':
#     executor2 = RobotExecutor(
#         json_path="titan_part2.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor2.run()
#     free_port(executor2.rr)

# # if __name__ == '__main__':
#     executor3 = RobotExecutor(
#         json_path="titan_part12.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor3.run()
#     free_port(executor3.rr)

# # if __name__ == '__main__':
#     executor4 = RobotExecutor(
#         json_path="titan_part2.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor4.run()
#     free_port(executor4.rr)
# # if __name__ == '__main__':
#     executor7 = RobotExecutor(
#         json_path="titan_part14.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor7.run()
#     free_port(executor7.rr)

# # if __name__ == '__main__':
#     executor8 = RobotExecutor(
#         json_path="titan_part2.json",
#         offset_table={"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]},
#         robot_ip='localhost',
#         speed=1.6,
#         acceleration=0.6
#     )
#     executor8.run()


if __name__ == '__main__':
    executor("titan_part11.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    executor("titan_part2.json",  {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    executor("titan_part12.json",{"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    executor("titan_part2.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    # executor("titan_part13.json",{"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    # executor("titan_part2.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    # executor("titan_part14.json",{"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    # executor("titan_part2.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})