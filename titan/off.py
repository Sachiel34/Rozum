from api.robot_api import RobotAPI
import socket
from progr_command import RobotExecutor
import socket


def free_port(api) -> None:
    """Закрывает TCP-соединение с роботом."""
    if api.socket:
        try:
            api.socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            api.socket.close()
        finally:
            api.socket = None

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

def shutdown_robot(robot_ip = 'localhost'):
    
    rr = RobotAPI(ip = robot_ip)
    rr.init_robot() 
    rr.off()
    print('Manipulator is sleep')
    free_port(rr) 
    

if __name__ == '__main__':
    executor("end.json", {"5": [0.02, 0.0, 0.01], "18": [0.0, -0.01, 0.0]})
    shutdown_robot()
