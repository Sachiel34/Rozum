import time
import json
import math
from api.robot_api import RobotAPI
from parcer import Parcer


class RobotExecutor:
    """
    Класс-обёртка для выполнения алгоритма робота.
    Объект класса содержит:
      - parcer: Parcer, загружающий и формирующий algorithm_list
      - algorithm_list: результат обработки parcer.process_list()
      - RobotAPI: объект для управления роботом
      - speed, acceleration: параметры движения
    """

    def __init__(self,
                 json_path: str,
                 offset_table: dict = None,
                 robot_ip: str = 'localhost',
                 speed: float = 1.0,
                 acceleration: float = 0.5):
        # Инициализируем парсер команд
        self.parcer = Parcer(json_path=json_path, offset_table=offset_table or {})
        # Формируем список алгоритма
        self.algorithm_list = self.parcer.process_list()
        # Настраиваем API робота
        self.rr = RobotAPI(ip=robot_ip)
        self.speed = speed
        self.acceleration = acceleration
        self.gripper_state = []
        # Инициализация робота
        self.rr.init_robot()
        self.rr.hold()
        # Параметры полезной нагрузки и инструмента
        self.rr.set_payload(1.6, [-0.15, -0.15, 0.08])
        self.rr.set_tool([0, 0, 0, 0, 0, 0])

    def run(self):
        """Запускает выполнение алгоритма на роботе."""
        print('*** Запуск алгоритма ***')
        for block in self.algorithm_list:
            repeat, *commands = block
            for _ in range(repeat):
                for cmd in commands:
                    for pt in cmd.get("points", []):
                        # Обработка ожидания
                        if "wait" in pt:
                            self.rr.run_wps()
                            self.rr.await_motion()
                            time.sleep(pt["wait"] / 1000)
                            continue
                        # Обработка движения по позе
                        if pt.get("pose") is not None:
                            self.rr.add_wp(
                                des_q=pt["pose"],
                                vmax_j=self.speed,
                                amax_j=self.acceleration,
                                rblend=0.7
                            )
                        # Обработка грипера
                        if "gripper" in pt:
                            self.rr.run_wps()
                            self.rr.await_motion()
                            gripperInputs = [0, 0, 0]
                            gripperInputs[pt["gripper"]] = 1
                            for i in range(3):
                                self.rr.write_dig_output(i + 8, gripperInputs[i])
                                # print(gripperInputs[i])
                            time.sleep(0.5)
                            n = pt["gripper"]
                        if pt.get("id") in self.gripper_state:
                            self.rr.run_wps()
                            self.rr.await_motion()
                            gripperInputs = [0, 0, 0]
                            n = abs(n - 1)
                            gripperInputs[n] = 1
                            for i in range(3):
                                self.rr.write_dig_output(i + 8, gripperInputs[i])
                                # print(gripperInputs[i])
                            time.sleep(0.5)
        # Финальный запуск и завершение
        self.rr.run_wps()
        self.rr.await_motion()
        time.sleep(0.5)
        # print('*** Алгоритм завершён ***')
