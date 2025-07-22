import subprocess
import sys

# CTRLR_COMS_POWER = 5
# POWER_CMD_ON = 3

def main():
    # 1) Запуск первого скрипта
    print("▶️ Запускаем первую часть")
    result1 = subprocess.run(
        [sys.executable, "titan00.py"],
        check=False  # не выбрасывать исключение при коде возврата ≠ 0
    )
    print(f" Первая часть завершилась{result1.returncode}\n")

    # 2) Всегда запускаем второй скрипт
    print("▶️ Запускаем вторую часть")
    result2 = subprocess.run(
        [sys.executable, "titan05.py"],
        check=False
    )
    print(f" Вторая часть завершилась {result2.returncode}")

if __name__ == "__main__":
    main()
