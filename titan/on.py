import socket
import time
from api.robot_api import RobotAPI
from progr_command import RobotExecutor

def free_port(api):
    """
    Освобождает порт, *не отключая* питание робота:
      • корректно рвём текущий TCP-сеанс;
      • обнуляем ссылку api.socket, чтобы RobotAPI создал
        новое соединение при следующем _connect().
    """
    if api.socket:
        try:
            print("Port is released")
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
    print('Algorithm complete')
    free_port(executor.rr)  

def init_robot(robot_ip = 'localhost'):
    
    rr = RobotAPI(ip = robot_ip)
    rr.init_robot()
    rr.run()
    rr.hold()
    
    print('Connection complete!')
    free_port(rr) 

if __name__ == '__main__':
    init_robot()
    print('Warning! Robot will start moving in 5 seconds')    
    time.sleep(5)
    executor("start.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    print('Ready to work')