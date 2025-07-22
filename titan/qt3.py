import sys
import os
import signal
import subprocess
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt

class RobotExecutorApp(QWidget):
    """Графический лаунчер для анодирования с отображением и редактированием параметров."""
    def __init__(self):
        super().__init__()
        # Настройка окна
        self.setWindowTitle("Robot Executor Launcher")
        self.setGeometry(300, 200, 520, 540)
        self.setStyleSheet(
            """
            background-color: rgb(240,240,240);
            font-family: Arial, sans-serif;
            font-size: 16px;
            """
        )
        self.layout = QVBoxLayout(self)

        # Заголовок
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

        # Чтение текущих параметров из loop.py
        self.current_steps = 0
        self.current_second = 0
        try:
            text = open("loop.py", "r", encoding="utf-8").read()
            m1 = re.search(r"^steps\s*=\s*(\d+)", text, flags=re.MULTILINE)
            m2 = re.search(r"^second\s*=\s*(\d+)", text, flags=re.MULTILINE)
            if m1:
                self.current_steps = int(m1.group(1))
            if m2:
                self.current_second = int(m2.group(1))
        except FileNotFoundError:
            pass

        # Режим просмотра (метки + кнопка Изменить)
        self.summary_widget = QWidget()
        summary_layout = QHBoxLayout(self.summary_widget)
        summary_layout.setContentsMargins(6, 10, 0, 0)
        labels_layout = QVBoxLayout()
        self.voltage_label = QLabel(f"Текущий вольтаж: {self.current_steps}")
        labels_layout.addWidget(self.voltage_label)
        self.time_label = QLabel(f"Текущее время анодирования: {self.current_second}")
        labels_layout.addWidget(self.time_label)
        summary_layout.addLayout(labels_layout)
        summary_layout.addStretch(1)
        self.edit_button = QPushButton("Изменить")
        # self.edit_button.setStyleSheet("background-color: rgb(139,25,155);")
        self.edit_button.setStyleSheet("height:150px; width:150px; margin-bottom:6px;background-color: rgb(152,141,242); border-radius:10px; border: 2px solid #007F00;")
        
        self.edit_button.clicked.connect(self._enter_edit_mode)
        summary_layout.addWidget(self.edit_button, 0, Qt.AlignTop)
        self.layout.addWidget(self.summary_widget)

        # Режим редактирования (поля + кнопка Подтвердить)
        self.edit_widget = QWidget()
        edit_layout = QHBoxLayout(self.edit_widget)
        edit_layout.setContentsMargins(6, 10, 0, 0)
        field_layout = QVBoxLayout()
        self.steps_input = QLineEdit()
        self.steps_input.setFixedWidth(300)
        self.steps_input.setPlaceholderText("Макс. вольтаж")
        self.steps_input.setStyleSheet("height:40px; width:300px; margin-bottom:6px;border-radius:10px; border: 2px solid #007F00;")
        field_layout.addWidget(self.steps_input)
        self.second_input = QLineEdit()
        self.second_input.setFixedWidth(300)
        self.second_input.setPlaceholderText("Время анодир.")
        self.second_input.setStyleSheet("height:40px; width:300px; margin-bottom:6px;border-radius:10px; border: 2px solid #007F00;")
        field_layout.addWidget(self.second_input)
        edit_layout.addLayout(field_layout)
        edit_layout.addSpacing(20)
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.setStyleSheet("height:150px; width:150px; margin-bottom:6px;border-radius:10px; border: 2px solid #007F00;")
        
        self.confirm_button.clicked.connect(self._apply_changes)
        edit_layout.addWidget(self.confirm_button, 0, Qt.AlignTop)
        edit_layout.addStretch(1)
        self.layout.addWidget(self.edit_widget)
        self.edit_widget.hide()

        # Метка обратного отсчета времени
        self.time_left_label = QLabel("")
        self.time_left_label.setStyleSheet("margin-top:4px;")
        self.layout.addWidget(self.time_left_label)

        # Сетка кнопок ячеек
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
            btn.setStyleSheet(
                """
                background-color: rgb(144,238,144);
                font-size:18px;
                height:80px;
                width:80px;
                border-radius:15px;
                border: 2px solid #007F00;
                """
            )
            btn.clicked.connect(self.create_pair_handler(script))
            grid.addWidget(btn, r, c)
            c = (c + 1) % 2
            if c == 0:
                r += 1
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        self.layout.addLayout(grid)

        # Кнопка "Все ячейки"
        self.all_button = QPushButton("Все ячейки")
        self.all_button.setStyleSheet(
            """
            background-color: rgb(144,238,144);
            font-size:18px;
            height:46px;
            width:200px;
            border-radius:20px;
            margin-top:12px;
            border: 2px solid #007F00;
            """
        )
        self.all_button.clicked.connect(self.run_all)
        self.layout.addWidget(self.all_button)

        # Кнопка "Стоп"
        self.stop_button = QPushButton("Стоп")
        self.stop_button.setStyleSheet(
            """
            background-color: rgb(255,0,0);
            font-size:22px;
            height:60px;
            width:200px;
            border-radius:15px;
            margin-top:20px;
            border: 3px solid #8B0000;
            """
        )
        self.stop_button.clicked.connect(self.stop_processes)
        self.layout.addWidget(self.stop_button)

        # Инициализация таймера и процессов
        self.running_processes = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_time_left)
        self.remaining_sec = 0

    def _enter_edit_mode(self):
        """Очищаем поля и переходим в режим редактирования."""
        self.summary_widget.hide()
        self.steps_input.clear()
        self.second_input.clear()
        self.steps_input.setFocus()
        self.edit_widget.show()

    def _apply_changes(self):
        """Сохраняем новые значения и возвращаемся в режим просмотра."""
        s = self.steps_input.text().strip()
        t = self.second_input.text().strip()
        if not (s.isdigit() and t.isdigit()):
            self.voltage_label.setText("Ошибка ввода!")
            return
        self.current_steps = int(s)
        self.current_second = int(t)
        try:
            data = open("loop.py", "r", encoding="utf-8").read()
            data = re.sub(r"^steps\s*=\s*\d+", f"steps = {self.current_steps}", data, flags=re.MULTILINE)
            if re.search(r"^second\s*=", data, flags=re.MULTILINE):
                data = re.sub(r"^second\s*=\s*\d+", f"second = {self.current_second}", data, flags=re.MULTILINE)
            else:
                data = re.sub(r"^steps.*$", lambda m: m.group(0) + f"\nsecond = {self.current_second}",
                              data, count=1, flags=re.MULTILINE)
            open("loop.py", "w", encoding="utf-8").write(data)
        except Exception:
            pass
        self.voltage_label.setText(f"Текущий вольтаж: {self.current_steps}")
        self.time_label.setText(f"Текущее время анодирования: {self.current_second}")
        self.edit_widget.hide()
        self.summary_widget.show()

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

    def stop_processes(self):
        self.label.setText("Остановка процессов…")
        for p in self.running_processes:
            if p.poll() is None:
                os.kill(p.pid, signal.SIGINT)
        self.running_processes.clear()
        self.stop_countdown()

    def start_countdown(self):
        
        # Исправлен расчёт: шаги * время шага
        self.remaining_sec = round(self.current_steps*42.025) * 2 + self.current_second
        self.update_time_label()
        self.timer.start(1000)

    def stop_countdown(self):
        self.timer.stop()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotExecutorApp()
    window.show()
    sys.exit(app.exec_())
