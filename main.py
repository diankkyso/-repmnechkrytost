import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from weather_core import WeatherDiary

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("850x650")
        self.diary = WeatherDiary()
        self.filter_date_var = tk.StringVar()
        self.filter_temp_var = tk.StringVar()
        self.filter_date_var.trace_add("write", lambda *args: self.apply_filters())
        self.filter_temp_var.trace_add("write", lambda *args: self.apply_filters())
        self.create_widgets()
        self.refresh_table()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        add_frame = ttk.LabelFrame(self.root, text="Добавить запись о погоде", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(add_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(add_frame, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        ttk.Label(add_frame, text="Температура:").grid(row=1, column=0, sticky="w")
        self.temp_entry = ttk.Entry(add_frame, width=10)
        self.temp_entry.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(add_frame, text="Описание:").grid(row=2, column=0, sticky="w")
        self.desc_entry = ttk.Entry(add_frame, width=40)
        self.desc_entry.grid(row=2, column=1, sticky="w", padx=5)
        self.precip_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(add_frame, text="Осадки", variable=self.precip_var).grid(row=3, column=1, sticky="w")
        ttk.Button(add_frame, text="Добавить запись", command=self.add_record).grid(row=4, column=1, sticky="e")
        ttk.Separator(self.root).pack(fill="x", padx=10, pady=5)
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(filter_frame, text="По дате:").grid(row=0, column=0)
        ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15).grid(row=0, column=1)
        ttk.Label(filter_frame, text="Температура >=").grid(row=0, column=2)
        ttk.Entry(filter_frame, textvariable=self.filter_temp_var, width=8).grid(row=0, column=3)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=4)
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("id", width=40)
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)
        scrollbar = ttk.Scrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Button(self.root, text="Удалить выбранное", command=self.delete_record).pack(pady=5)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in self.diary.get_records():
            self.tree.insert("", "end", values=(record["id"], record["date"], record["temperature"], record["description"], "Да" if record["precipitation"] else "Нет"))

    def apply_filters(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        records = self.diary.get_records()
        date_filter = self.filter_date_var.get().strip()
        temp_filter = self.filter_temp_var.get().strip()
        if date_filter:
            records = [r for r in records if r["date"] == date_filter]
        if temp_filter:
            try:
                min_temp = float(temp_filter)
                records = [r for r in records if r["temperature"] >= min_temp]
            except ValueError:
                pass
        for record in records:
            self.tree.insert("", "end", values=(record["id"], record["date"], record["temperature"], record["description"], "Да" if record["precipitation"] else "Нет"))

    def reset_filters(self):
        self.filter_date_var.set("")
        self.filter_temp_var.set("")

    def add_record(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return
        if self.diary.add_record(date_str, temperature, description, precipitation):
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
            self.temp_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")
            self.precip_var.set(False)
            self.apply_filters()
            messagebox.showinfo("Успех", "Запись добавлена!")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        record_id = self.tree.item(selected[0], "values")[0]
        if self.diary.delete_record(int(record_id)):
            self.apply_filters()
            messagebox.showinfo("Успех", "Запись удалена!")

    def on_closing(self):
        self.diary.save_to_file()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()