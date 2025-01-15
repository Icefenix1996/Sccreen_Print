import tkinter as tk
from PIL import ImageGrab
from io import BytesIO
import win32clipboard
import firebase_admin
from firebase_admin import credentials, db
import datetime

# Инициализация Firebase
def init_firebase():
    try:
        if not firebase_admin._apps:  # Проверяем, инициализирован ли Firebase
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://screenshotapp-ed554-default-rtdb.europe-west1.firebasedatabase.app/"
            })
            print("Firebase успешно инициализирован!")
        else:
            print("Firebase уже инициализирован.")
    except Exception as e:
        print("Ошибка инициализации Firebase:", e)

# Функции работы с базой данных
def get_db_reference():
    try:
        return db.reference("users/screenshot_app")
    except Exception as e:
        print("Ошибка подключения к Firebase:", e)
        return None

def load_counter():
    try:
        db_ref = get_db_reference()
        count = db_ref.child("counter").get()
        if count is None:  # Если данных нет, инициализируем 0
            db_ref.child("counter").set(0)
            return 0
        return count
    except Exception as e:
        print("Ошибка загрузки данных из Firebase:", e)
        return 0

def save_counter(count):
    try:
        db_ref = get_db_reference()
        db_ref.child("counter").set(count)
    except Exception as e:
        print("Ошибка сохранения данных в Firebase:", e)

def log_click(count):
    try:
        db_ref = get_db_reference()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        db_ref.child("history").child(today).set(count)
    except Exception as e:
        print("Ошибка логирования кликов:", e)

def get_click_history():
    try:
        db_ref = get_db_reference()
        history = db_ref.child("history").get()
        return history if history else {}
    except Exception as e:
        print("Ошибка получения истории кликов:", e)
        return {}

# Функция для создания скриншота
def take_screenshot():
    global click_count
    # Делаем скриншот
    screenshot = ImageGrab.grab()
    output = BytesIO()
    screenshot.save(output, format="BMP")
    data = output.getvalue()[14:]  # Убираем заголовок BMP
    output.close()
    
    # Копируем изображение в буфер обмена
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
    print("Скриншот сделан и скопирован в буфер обмена!")

    # Увеличиваем и сохраняем счётчик
    click_count += 1
    save_counter(click_count)
    log_click(click_count)
    counter_label.config(text=f"Скриншотов сделано: {click_count}")

# Загружаем счётчик при запуске программы
init_firebase()
click_count = load_counter()

# Создание GUI
root = tk.Tk()
root.title("Скриншот с Firebase")
root.geometry("300x100")  # Фиксированный размер окна

# Кнопка для создания скриншота
screenshot_button = tk.Button(root, text="Сделать скриншот", font=("Arial", 14), command=take_screenshot)
screenshot_button.pack(pady=5)

# Метка для отображения количества скриншотов
counter_label = tk.Label(root, text=f"Скриншотов сделано: {click_count}", font=("Arial", 12))
counter_label.pack(pady=5)

# Кнопка для отображения истории
def show_history():
    history = get_click_history()
    history_window = tk.Toplevel()
    history_window.title("История")
    tk.Label(history_window, text="Дата: Количество").pack()
    for date, clicks in history.items():
        tk.Label(history_window, text=f"{date}: {clicks}").pack()

history_button = tk.Button(root, text="История", font=("Arial", 10), command=show_history)
history_button.pack(pady=5)

# Запуск приложения
root.mainloop()
