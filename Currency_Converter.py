import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
from datetime import datetime

# Глобальные переменные
history = []
history_file = "history.json"
api_url = "https://api.exchangerate-api.com/v4/latest/"


def load_history():
    global history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    else:
        history = []


def save_history():
    #Сохранение истории в файл
    global history
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except:
        pass


def update_history_display(history_listbox):
    #Обновление отображения истории
    history_listbox.delete(0, tk.END)
    for entry in history:
        history_listbox.insert(tk.END, entry)


def add_to_history(from_curr, to_curr, amount, result, rate, history_listbox):
    #Добавление записи в историю
    global history
    time_str = datetime.now().strftime("%H:%M:%S")
    history_entry = f"{time_str} | {amount:.2f} {from_curr} → {result:.2f} {to_curr} (курс: {rate:.4f})"

    history.insert(0, history_entry)

    # Ограничиваем 20 записями
    if len(history) > 20:
        history = history[:20]

    update_history_display(history_listbox)
    save_history()


def convert_currency(amount_entry, from_var, to_var, result_label, convert_btn, history_listbox):
    # Проверка суммы
    amount_str = amount_entry.get().strip()
    if not amount_str:
        messagebox.showwarning("Ошибка", "Введите сумму")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showwarning("Ошибка", "Сумма должна быть больше 0")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Введите число")
        return

    from_curr = from_var.get()
    to_curr = to_var.get()

    # Если валюты одинаковые
    if from_curr == to_curr:
        result = amount
        rate = 1.0
        result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
        add_to_history(from_curr, to_curr, amount, result, rate, history_listbox)
        return

    # Получаем курс
    convert_btn.config(state=tk.DISABLED, text="Загрузка...")

    try:
        response = requests.get(f"{api_url}{from_curr}", timeout=10)
        response.raise_for_status()
        data = response.json()

        rate = data['rates'].get(to_curr)
        if rate is None:
            messagebox.showerror("Ошибка", f"Валюта {to_curr} не найдена")
            return

        result = amount * rate
        result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
        add_to_history(from_curr, to_curr, amount, result, rate, history_listbox)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить курс: {str(e)}")
    finally:
        convert_btn.config(state=tk.NORMAL, text="Конвертировать")


def clear_history(history_listbox):
    global history
    if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
        history = []
        update_history_display(history_listbox)
        save_history()


def load_history_from_file(history_listbox):
    global history
    if os.path.exists(history_file):
        load_history()
        update_history_display(history_listbox)
        messagebox.showinfo("Информация", f"Загружено {len(history)} записей")
    else:
        messagebox.showinfo("Информация", "Файл истории не найден")


def main():
    # Создание окна
    root = tk.Tk()
    root.title("Конвертер Валют")
    root.geometry("450x400")
    root.resizable(False, False)

    # Список валют
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'RUB']

    # Загрузка истории
    load_history()

    # Сумма
    tk.Label(root, text="Сумма:", font=('Arial', 11)).place(x=50, y=30)
    amount_entry = tk.Entry(root, width=15)
    amount_entry.place(x=110, y=30)

    # Из валюты
    tk.Label(root, text="Из:", font=('Arial', 11)).place(x=50, y=70)
    from_var = tk.StringVar(value="USD")
    from_menu = tk.OptionMenu(root, from_var, *currencies)
    from_menu.place(x=110, y=65)

    # В валюту
    tk.Label(root, text="В:", font=('Arial', 11)).place(x=220, y=70)
    to_var = tk.StringVar(value="EUR")
    to_menu = tk.OptionMenu(root, to_var, *currencies)
    to_menu.place(x=250, y=65)

    # Результат
    result_label = tk.Label(root, text="", font=('Arial', 12, 'bold'), fg="blue")
    result_label.place(x=110, y=110)

    # Кнопка конвертации
    convert_btn = tk.Button(root, text="Конвертировать", width=20)
    convert_btn.place(x=130, y=150)

    # История
    tk.Label(root, text="История конвертаций:", font=('Arial', 10, 'bold')).place(x=50, y=200)

    # Список для истории
    history_listbox = tk.Listbox(root, width=50, height=8)
    history_listbox.place(x=50, y=230)

    # Скроллбар
    scrollbar = tk.Scrollbar(root, command=history_listbox.yview)
    scrollbar.place(x=380, y=230, height=130)
    history_listbox.config(yscrollcommand=scrollbar.set)

    # Кнопки истории
    tk.Button(root, text="Очистить", width=10, command=lambda: clear_history(history_listbox)).place(x=50, y=370)
    tk.Button(root, text="Сохранить", width=10, command=save_history).place(x=150, y=370)
    tk.Button(root, text="Загрузить", width=10, command=lambda: load_history_from_file(history_listbox)).place(x=250,
                                                                                                               y=370)

    # Настройка кнопки конвертации
    convert_btn.config(command=lambda: convert_currency(
        amount_entry, from_var, to_var, result_label, convert_btn, history_listbox
    ))

    # Привязка Enter
    amount_entry.bind('<Return>', lambda e: convert_currency(
        amount_entry, from_var, to_var, result_label, convert_btn, history_listbox
    ))

    # Заполняем историю
    update_history_display(history_listbox)

    # Запуск
    root.mainloop()

main()