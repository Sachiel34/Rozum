import sys
import os
import signal
import subprocess
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit
)
from PyQt5.QtCore import QTimer


class RobotExecutorApp(QWidget):
    """Графический лаунчер для анодирования.

    * Запускает одиночные скрипты titan_Xcell.py или launcher.py.
    * Показывает обратный отсчёт оставшегося времени.
    * Позволяет изменять параметры `steps` и `second` в loop.py через GUI.
    * Красная кнопка «Стоп» посылает SIGINT (Ctrl+C) всем запущенным процессам.
    """

    def __init__(self):
        super().__init__()

        # ----- базовые настройки окна -----
        self.setWindowTitle("Robot Executor Launcher")
        self.setGeometry(300, 200, 520, 540)
        self.setStyleSheet(
            """
            background-color: rgb(240,240,240);
            font-family: Arial, sans-serif;
            font-size: 16px;
            """
        )

        self.layout = QVBoxLayout()

        # ----- заголовок -----
        self.label = QLabel("Выберите действия для запуска робота")
        self.label.setStyleSheet(
            """
            background-color: rgb(200,200,255);
            padding: 10px;
            border: 2px solid rgb(100,100,200);
            border-radius: 10px;
            """
        )
        self.layout.addWidget(self.label)

        # ----- ввод параметров -----
        self.steps_input = QLineEdit()
        self.steps_input.setPlaceholderText("Введите количество шагов (steps)")
        self.steps_input.setStyleSheet("height:28px; margin-bottom:6px;")
        self.layout.addWidget(self.steps_input)

        self.second_input = QLineEdit()
        self.second_input.setPlaceholderText("Введите время шага в секундах (second)")
        self.second_input.setStyleSheet("height:28px; margin-bottom:6px;")
        self.layout.addWidget(self.second_input)

        # ----- кнопка Подтвердить -----
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.setStyleSheet(
            """
            background-color: rgb(100,200,255);
            font-size: 17px;
            height:40px; border-radius:8px;
            """
        )
        self.confirm_button.clicked.connect(self.update_loop_parameters)
        self.layout.addWidget(self.confirm_button)

        # ----- метка обратного отсчёта -----
        self.time_left_label = QLabel("")
        self.time_left_label.setStyleSheet("margin-top:4px;")
        self.layout.addWidget(self.time_left_label)

        # ----- сетка кнопок ячеек -----
        grid = QGridLayout()
        self.pair_buttons = [
            ("1 ячейка", "titan_1cell.py"),
            ("2 ячейка", "titan_2cell.py"),
            ("3 ячейка", "titan_3cell.py"),
            ("4 ячейка", "titan_4cell.py"),
        ]
        r = c = 0
        for text, script in self.pair_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(120, 120)
            btn.setStyleSheet(
                """
                background-color: rgb(144,238,144);
                font-size:18px; border-radius:10px;
                """
            )
            btn.clicked.connect(self.create_pair_handler(script))
            grid.addWidget(btn, r, c)
            c = (c + 1) % 2
            if c == 0:
                r += 1
        self.layout.addLayout(grid)

        # ----- кнопка Все ячейки -----
        self.all_button = QPushButton("Все ячейки")
        self.all_button.setStyleSheet(
            """
            background-color: rgb(144,238,144);
            font-size:18px; height:46px; border-radius:10px; margin-top:12px;
            """
        )
        self.all_button.clicked.connect(self.run_all)
        self.layout.addWidget(self.all_button)


        # ----- кнопка Стоп -----
        self.stop_button = QPushButton("Стоп")
        self.stop_button.setStyleSheet(
            """
            background-color: rgb(255,0,0);
            font-size:20px; height:60px; border-radius:10px; margin-top:20px;
            """
        )
        self.stop_button.clicked.connect(self.stop_processes)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

        # ----- внутренние переменные -----
        self.running_processes = []      # список subprocess.Popen
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_time_left)
        self.remaining_sec = 0
        # дефолтные значения до подтверждения
        self.current_steps = 1261
        self.current_second = 1

    # ------------------------------------------------------------------
    # ------------------------  запуск скриптов  ------------------------
    # ------------------------------------------------------------------
    def create_pair_handler(self, script):
        def handler():
            self.start_countdown()
            self.launch_script(script)
        return handler

    def run_all(self):
        self.start_countdown()
        self.launch_script("launcher.py")

    def launch_script(self, script):
        self.label.setText(f"Запуск: {script}")
        proc = subprocess.Popen([sys.executable, script])
        self.running_processes.append(proc)

    # ------------------------------------------------------------------
    # -------------------  остановка процессов  ------------------------
    # ------------------------------------------------------------------
    def stop_processes(self):
        self.label.setText("Остановка процессов…")
        for p in self.running_processes:
            if p.poll() is None:  # процесс жив
                os.kill(p.pid, signal.SIGINT)
        self.running_processes.clear()
        self.stop_countdown()

    # ------------------------------------------------------------------
    # ---------------- изменения в loop.py -----------------------------
    # ------------------------------------------------------------------
    def update_loop_parameters(self):
        steps_txt = self.steps_input.text().strip()
        sec_txt = self.second_input.text().strip()

        if not (steps_txt.isdigit() and sec_txt.isdigit()):
            self.label.setText("Ошибка: введите целые числа.")
            return

        self.current_steps = int(steps_txt)
        self.current_second = int(sec_txt)

        with open("loop.py", "r", encoding="utf-8") as f:
            code = f.read()

        # обновляем steps
        code = re.sub(r"^steps\s*=\s*\d+", f"steps = {self.current_steps}", code, flags=re.MULTILINE)

        # обновляем или добавляем second
        if re.search(r"^second\s*=", code, flags=re.MULTILINE):
            code = re.sub(r"^second\s*=\s*\d+", f"second = {self.current_second}", code, flags=re.MULTILINE)
        else:
            # вставить после строки с steps
            code = re.sub(r"^steps\s*=.*$", lambda m: m.group(0) + f"\nsecond = {self.current_second}", code, count=1, flags=re.MULTILINE)

        with open("loop.py", "w", encoding="utf-8") as f:
            f.write(code)

        self.label.setText(
            f"Параметры обновлены: steps = {self.current_steps}, second = {self.current_second}"
        )

    # ------------------------------------------------------------------
    # -------------------  обратный отсчёт времени  --------------------
    # ------------------------------------------------------------------
    def start_countdown(self):
        # 2 «горки» + пауза 2700 с
        self.remaining_sec = self.current_steps * 2 + self.current_second
        self.update_time_label()
        self.timer.start(1000)

    def stop_countdown(self):
        self.timer.stop()
        self.time_left_label.setText("")


    def tick_time_left(self):
        if self.remaining_sec > 0:
            self.remaining_sec -= 1
            self.update_time_label()
        else:
            self.stop_countdown()

    def update_time_label(self):    
        h = self.remaining_sec // 3600
        m = (self.remaining_sec % 3600) // 60
        s = self.remaining_sec % 60
        self.time_left_label.setText(f"Оставшееся время: {h:02d}:{m:02d}:{s:02d}")


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotExecutorApp()
    window.show()
    sys.exit(app.exec_())
