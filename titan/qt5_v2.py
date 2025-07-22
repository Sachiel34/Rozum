import sys
import os
import signal
import subprocess
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor


# ---------- Helpers ------------------------------------------------------------------ #
def _make_shadow(blur: int, offset_y: int, alpha: int) -> QGraphicsDropShadowEffect:
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, offset_y)
    eff.setColor(QColor(0, 0, 0, alpha))
    return eff


def add_shadow(button: QPushButton):
    """Динамический drop-shadow, который усиливается при нажатии."""
    normal_eff = _make_shadow(10, 3, 120)
    pressed_eff = _make_shadow(4, 1, 200)
    button.setGraphicsEffect(normal_eff)
    button.pressed.connect(lambda: button.setGraphicsEffect(pressed_eff))
    button.released.connect(lambda: button.setGraphicsEffect(normal_eff))


def build_style(normal_rgb: str, pressed_rgb: str, extra: str = "") -> str:
    """Создаёт стиль QPushButton (обычный и :pressed)."""
    return f"""
QPushButton{{
    background-color: {normal_rgb};
    {extra}
}}
QPushButton:pressed{{
    background-color: {pressed_rgb};
}}
"""


# ---------- Main window -------------------------------------------------------------- #
class RobotExecutorApp(QWidget):
    """Графический лаунчер с выбором ячеек и параметров."""

    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowTitle("Robot Executor Launcher")
        self.setFixedWidth(380)
        self.setFixedHeight(560)
        self.setStyleSheet(
            """
            background-color: rgb(255, 250, 240);
            font-family: Arial, sans-serif;
            font-size: 18px;
            """
        )
        self.layout = QVBoxLayout(self)

        # ---------- Верхняя панель ---------------------------------------------------- #
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 6)
        header_layout.setSpacing(20)

        self.label = QLabel("Choose action:")
        self.label.setFixedWidth(220)
        self.label.setStyleSheet(
            """
            background-color: rgb(235, 199, 223);
            padding: 10px;
            border: 2px solid rgb(100,100,200);
            border-radius: 10px;
            """
        )
        header_layout.addWidget(self.label)
        header_layout.addStretch(1)

        self.toggle_button = QPushButton("ON")
        self.toggle_button.setFixedSize(80, 80)
        self.toggle_button.setStyleSheet(build_style(
            "rgb(159,226,191)", "rgb(159,226,191)",
            "border-radius:12px; font-size:14px; border:2px solid #009b76;"
        ))
        add_shadow(self.toggle_button)
        self.toggle_button.clicked.connect(self._toggle_action)
        header_layout.addWidget(self.toggle_button)
        self.layout.addWidget(header_widget)

        # ---------- Чтение базовых параметров ----------------------------------------- #
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

        # ---------- Вид «просмотр» ---------------------------------------------------- #
        self.summary_widget = QWidget()
        summary_layout = QHBoxLayout(self.summary_widget)
        summary_layout.setContentsMargins(6, 10, 0, 0)

        labels_layout = QVBoxLayout()
        self.voltage_label = QLabel(f"Current Voltage: {self.current_steps}")
        labels_layout.addWidget(self.voltage_label)
        self.time_label = QLabel(f"Current anodizing time: {self.current_second}")
        labels_layout.addWidget(self.time_label)
        summary_layout.addLayout(labels_layout)
        summary_layout.addStretch(1)

        self.edit_button = QPushButton("Change")
        self.edit_button.setStyleSheet(build_style(
            "rgb(175, 238, 238)", "rgb(133,229,229)",
            "height:100px; width:100px; margin-bottom:6px; "
            "border-radius:10px; border:2px solid #7dc1e3; font-size:16px;"
        ))
        add_shadow(self.edit_button)
        self.edit_button.clicked.connect(self._enter_edit_mode)
        summary_layout.addWidget(self.edit_button, 0, Qt.AlignTop)
        self.layout.addWidget(self.summary_widget)

        # ---------- Вид «редактирование» --------------------------------------------- #
        self.edit_widget = QWidget()
        edit_layout = QHBoxLayout(self.edit_widget)
        edit_layout.setContentsMargins(6, 10, 0, 0)

        field_layout = QVBoxLayout()
        self.steps_input = QLineEdit()
        self.steps_input.setFixedWidth(220)
        self.steps_input.setPlaceholderText("Max Voltage(V)")
        self.steps_input.setStyleSheet(
            "height:40px; width:300px; margin-bottom:6px; "
            "border-radius:10px; border:2px solid #B0E0E6;"
        )
        field_layout.addWidget(self.steps_input)

        self.second_input = QLineEdit()
        self.second_input.setFixedWidth(220)
        self.second_input.setPlaceholderText("Anodizing time(sec)")
        self.second_input.setStyleSheet(
            "height:40px; width:300px; margin-bottom:6px; "
            "border-radius:10px; border:2px solid #B0E0E6;"
        )
        field_layout.addWidget(self.second_input)

        edit_layout.addLayout(field_layout)
        edit_layout.addSpacing(20)

        self.confirm_button = QPushButton("Config")
        self.confirm_button.setStyleSheet(build_style(
            "rgb(255, 207, 171)", "rgb(215,180,150)",
            "height:100px; width:100px; margin-bottom:6px; "
            "border-radius:10px; border:2px solid #ff9545; font-size:16px;"
        ))
        add_shadow(self.confirm_button)
        self.confirm_button.clicked.connect(self._apply_changes)
        edit_layout.addWidget(self.confirm_button, 0, Qt.AlignTop)
        edit_layout.addStretch(1)
        self.layout.addWidget(self.edit_widget)
        self.edit_widget.hide()

        # ---------- Таймер обратного отсчёта ---------------------------------------- #
        self.time_left_label = QLabel("")
        self.time_left_label.setStyleSheet("margin-top:4px;")
        self.layout.addWidget(self.time_left_label)

        # ---------- Кнопки ячеек + управление (3×2) ---------------------------------- #
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self.selected_scripts = []
        self.pending_scripts = []
        self.cell_buttons = []           # <— добавлено: список кнопок для сброса стиля

        cell_defs = [
            ("1 cell", "titan_1cell.py"),
            ("2 cell", "titan_2cell.py"),
            ("3 cell", "titan_3cell.py"),
            ("4 cell", "titan_4cell.py"),
        ]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (text, script), (r, c) in zip(cell_defs, positions):
            btn_style = build_style(
                "rgb(240,255,240)", "rgb(120,200,120)",
                "font-size:18px; height:60px; width:60px; "
                "border-radius:15px; border:2px solid #007F00;"
            )
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            btn.original_style = btn_style
            add_shadow(btn)
            btn.clicked.connect(lambda chk, b=btn, s=script: self.toggle_selection(b, s))
            grid.addWidget(btn, r, c)
            self.cell_buttons.append((btn, script))   # <— сохраняем

        # --- Кнопка «Запустить выбранные» ------------------------------------------- #
        self.run_selected_button = QPushButton("Start")
        self.run_selected_button.setStyleSheet(build_style(
            "rgb(240,255,240)", "rgb(120,200,120)",
            "font-size:18px; height:60px; width:60px; "
            "border-radius:15px; border:2px solid #007F00;"
        ))
        add_shadow(self.run_selected_button)
        self.run_selected_button.clicked.connect(self.run_selected)
        grid.addWidget(self.run_selected_button, 2, 1)

        # --- Кнопка «All cells» ------------------------------------------------------ #
        self.all_button = QPushButton("All cells")
        self.all_button.setStyleSheet(build_style(
            "rgb(240,255,240)", "rgb(120,200,120)",
            "font-size:18px; height:60px; width:60px; "
            "border-radius:15px; border:2px solid #007F00;"
        ))
        add_shadow(self.all_button)
        self.all_button.clicked.connect(self.run_all)
        grid.addWidget(self.all_button, 2, 0)

        for col in range(2):
            grid.setColumnStretch(col, 1)
        for row in range(3):
            grid.setRowStretch(row, 1)

        self.layout.addLayout(grid)

        # ---------- Кнопка «Стоп» ---------------------------------------------------- #
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(build_style(
            "rgb(204,0,0)", "rgb(200,0,0)",
            "font-size:22px; height:60px; width:200px; "
            "border-radius:15px; margin-top:16px; border:2px solid #8B0000;"
        ))
        add_shadow(self.stop_button)
        self.stop_button.clicked.connect(self.stop_processes)
        self.layout.addWidget(self.stop_button)

        # ---------- Сервисные переменные -------------------------------------------- #
        self.running_processes = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_time_left)
        self.remaining_sec = 0

    # ---------- Режим редактирования параметров ------------------------------------- #
    def _enter_edit_mode(self):
        self.summary_widget.hide()
        self.steps_input.clear()
        self.second_input.clear()
        self.steps_input.setFocus()
        self.edit_widget.show()

    def _apply_changes(self):
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
                data = re.sub(r"^steps.*$",
                              lambda m: m.group(0) + f"\nsecond = {self.current_second}",
                              data, count=1, flags=re.MULTILINE)
            open("loop.py", "w", encoding="utf-8").write(data)
        except Exception:
            pass

        self.voltage_label.setText(f"Current Voltage: {self.current_steps}")
        self.time_label.setText(f"Anodizing time: {self.current_second}")

        self.edit_widget.hide()
        self.summary_widget.show()

    # ---------- Логика выбора/запуска ячеек ----------------------------------------- #
    def toggle_selection(self, btn: QPushButton, script: str):
        if script in self.selected_scripts:
            self.selected_scripts.remove(script)
            btn.setStyleSheet(btn.original_style)
        else:
            self.selected_scripts.append(script)
            btn.setStyleSheet(build_style(
                "rgb(255, 255, 153)", "rgb(255, 255, 100)",
                "font-size:18px; height:60px; width:60px; "
                "border-radius:15px; border:2px solid #FFA500;"
            ))

    def run_selected(self):
        if not self.selected_scripts:
            self.label.setText("No cells selected")
            return
        self.pending_scripts = list(self.selected_scripts)
        next_script = self.pending_scripts.pop(0)
        self.start_countdown()
        self.launch_script(next_script)

    def run_all(self):
        self.start_countdown()
        self.launch_script("launcher.py")

    def launch_script(self, script: str):
        self.label.setText(f"Start: {script}")
        proc = subprocess.Popen([sys.executable, script])
        self.running_processes.append(proc)

    # ---------- Управление процессами ----------------------------------------------- #
    def stop_processes(self):
        """Останавливает процессы и сбрасывает всё выделение."""
        self.label.setText("Stopping the process")
        # Завершаем дочерние процессы
        for p in self.running_processes:
            if p.poll() is None:
                os.kill(p.pid, signal.SIGINT)
        self.running_processes.clear()
        self.stop_countdown()
        self.pending_scripts.clear()

        # --- Снимаем выделение ячеек ---
        self.selected_scripts.clear()
        for btn, _ in self.cell_buttons:
            btn.setStyleSheet(btn.original_style)

    # ---------- Таймер ---------------------------------------------------------------- #
    def start_countdown(self):
        self.remaining_sec = round(self.current_steps * 42.025) * 2 + \
                             self.current_second + 75 + 102 + 10
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
            if self.pending_scripts:
                next_script = self.pending_scripts.pop(0)
                self.start_countdown()
                self.launch_script(next_script)

    def update_time_label(self):
        h = self.remaining_sec // 3600
        m = (self.remaining_sec % 3600) // 60
        s = self.remaining_sec % 60
        self.time_left_label.setText(f"Remaining time: {h:02d}:{m:02d}:{s:02d}")

    # ---------- ON / OFF ------------------------------------------------------------- #
    def _toggle_action(self):
        if self.toggle_button.text() == "ON":
            subprocess.Popen([sys.executable, "on.py"])
            self.toggle_button.setText("OFF")
            self.toggle_button.setStyleSheet(build_style(
                "rgb(255,142,122)", "rgb(255,142,122)",
                "border-radius:12px; font-size:14px;border:2px solid #ff6347;"
            ))
        else:
            subprocess.Popen([sys.executable, "off.py"])
            self.toggle_button.setText("ON")
            self.toggle_button.setStyleSheet(build_style(
                "rgb(159,226,191)", "rgb(159,226,191)",
                "border-radius:12px; font-size:14px;border:2px solid #009b76;"
            ))


# ---------- Entry-point -------------------------------------------------------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotExecutorApp()
    window.show()
    sys.exit(app.exec_())
