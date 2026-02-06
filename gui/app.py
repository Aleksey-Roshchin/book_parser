import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from parser.core import parse_book


def start_parsing():
    url = url_entry.get().strip()
    folder = folder_entry.get().strip()

    if not url:
        messagebox.showerror("Ошибка", "Введите URL первой страницы")
        return

    if not folder:
        messagebox.showerror("Ошибка", "Выберите папку для сохранения")
        return

    start_button.config(state="disabled")

    def gui_log(msg):
        log_text.after(0, lambda: (
            log_text.insert("end", msg + "\n"),
            log_text.see("end")
        ))

    def worker():
        try:
            parse_book(url, folder, log=gui_log)
            gui_log("=== Готово ===")
        except Exception as e:
            gui_log(f"Ошибка: {e}")
        finally:
            start_button.after(0, lambda: start_button.config(state="normal"))

    threading.Thread(target=worker, daemon=True).start()


def choose_folder():
    path = filedialog.askdirectory()
    if path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, path)


root = tk.Tk()
root.title("Book Parser")
root.geometry("700x500")

# URL
tk.Label(root, text="URL первой страницы:").pack(anchor="w", padx=10, pady=(10, 0))
url_entry = tk.Entry(root)
url_entry.pack(fill="x", padx=10)

# Folder
tk.Label(root, text="Папка для сохранения:").pack(anchor="w", padx=10, pady=(10, 0))
folder_frame = tk.Frame(root)
folder_frame.pack(fill="x", padx=10)

folder_entry = tk.Entry(folder_frame)
folder_entry.pack(side="left", fill="x", expand=True)

tk.Button(folder_frame, text="Обзор…", command=choose_folder).pack(side="right", padx=5)

# Start button
start_button = tk.Button(root, text="Начать парсинг", command=start_parsing)
start_button.pack(pady=10)

# Log
tk.Label(root, text="Лог:").pack(anchor="w", padx=10)
log_text = tk.Text(root, height=15)
log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

root.mainloop()
