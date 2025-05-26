import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os

selected_file_path = None  # Глобальная переменная для пути к выбранному файлу
data = {}  # Глобальная переменная для хранения данных


def choose_data_file():
    """Функция выбора файла через диалог"""
    global selected_file_path
    file_path = filedialog.askopenfilename(
        title="Выберите файл для работы",
        filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
    )

    if not file_path:
        if messagebox.askyesno("Важно", "Вы не выбрали файл. Использовать дефолтный data.json?"):
            file_path = "data.json"
        else:
            return False

    selected_file_path = file_path
    return True


def initialize_data(file_path):
    """Инициализация данных из выбранного файла"""
    global data
    if not os.path.exists(file_path):
        # Создаем файл с начальными данными
        data = {
            'users': [
                {'login': 'user', 'password': 'user', 'contact': 'user@example.com', 'role': 'user'},
                {'login': 'admin', 'password': 'admin', 'contact': 'admin@example.com', 'role': 'admin'}
            ],
            'contractors': ['Строительный Дом', 'Мастер-Ремонт', 'Уютный Дом', 'РемонтСервис', 'ДомСтрой'],
            'materials': {
                'Гипсокартон': 150,
                'Декоративная штукатурка': 300,
                'Полимерная плитка': 250,
                'Ламинат Lamington': 200,
                'Экошпон': 400
            },
            'objects': ['Квартира', 'Офис', 'Торговый центр', 'Дачный дом', 'Таунхаус'],
            'types_of_work': [
                'Штукатурка стен',
                'Укладка плитки',
                'Монтаж натяжных потолков',
                'Монтаж электропроводки',
                'Установка сантехники'
            ],
            'orders': [],
            'order_statuses': ['В обработке', 'Выполнен', 'Отменен', 'Ожидает подтверждения']
        }
        with open(file_path, 'w') as f:
            json.dump(data, f)
    else:
        with open(file_path, 'r') as f:
            data = json.load(f)


def save_data():
    """Сохранение данных в выбранный файл"""
    with open(selected_file_path, 'w') as f:
        json.dump(data, f)


# Основной блок выбора файла
def show_file_chooser():
    """Окно выбора файла"""
    root_temp = tk.Tk()
    root_temp.title("Выбор файла")
    root_temp.geometry("400x200")

    def proceed():
        global selected_file_path
        if choose_data_file():
            root_temp.destroy()
            initialize_data(selected_file_path)
            main_app()  # Запуск основного приложения
        else:
            messagebox.showwarning("Ошибка", "Файл не выбран")

    ttk.Label(root_temp, text="Выберите файл для работы с данными:").pack(pady=20)
    ttk.Button(root_temp, text="Выбрать файл", command=proceed).pack(pady=10)

    root_temp.mainloop()

work_type_multiplier = {
    'Штукатурка стен': 1.2,
    'Укладка плитки': 2.0,
    'Монтаж натяжных потолков': 2.5,
    'Монтаж электропроводки': 3.0,
    'Установка сантехники': 1.8
}

def main_app():
    """Основное приложение"""
    global current_user, root
    current_user = None

    def register_user():
        login = simpledialog.askstring("Регистрация", "Введите логин:")
        if any(u['login'] == login for u in data['users']):
            return messagebox.showerror("Ошибка", "Логин занят!")

        password = simpledialog.askstring("Регистрация", "Введите пароль:", show='*')
        contact = simpledialog.askstring("Регистрация", "Введите контактные данные:")

        if login and password and contact:
            data['users'].append({'login': login, 'password': password, 'contact': contact, 'role': 'user'})
            save_data()
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля!")

    def login_window():
        def login():
            login_val = login_entry.get()
            password_val = password_entry.get()
            global current_user
            for user in data['users']:
                if user['login'] == login_val and user['password'] == password_val:
                    current_user = user
                    messagebox.showinfo("Успех", "Вход успешен!")
                    login_dialog.destroy()
                    update_main_buttons()
                    return
            messagebox.showerror("Ошибка", "Неверные учетные данные!")

        login_dialog = tk.Toplevel(root)
        login_dialog.title("Вход")
        login_dialog.geometry("300x150")

        ttk.Label(login_dialog, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        login_entry = ttk.Entry(login_dialog)
        login_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_dialog, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(login_dialog, show='*')
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(login_dialog, text="Войти", command=login).grid(row=2, columnspan=2, pady=10)

    def logout():
        global current_user
        current_user = None
        update_main_buttons()
        messagebox.showinfo("Успех", "Вы вышли из системы!")

    def create_order_window():
        if not current_user:
            return messagebox.showerror("Ошибка", "Вы не вошли в систему!")

        def create_order():
            contractor = contractor_var.get()
            selected_materials = [item for item in materials_listbox.curselection()]
            materials = [materials_listbox.get(i) for i in selected_materials]
            material_cost = sum(data['materials'][m] for m in materials)
            obj = object_var.get()
            work_type = work_type_var.get()
            try:
                customer_price = float(customer_price_entry.get())
                area = float(area_entry.get())
            except ValueError:
                return messagebox.showerror("Ошибка", "Введите числа в полях цены и площади")

            cost = material_cost + work_type_multiplier[work_type] * customer_price * area

            order = {
                'contractor': contractor,
                'materials': materials,
                'object': obj,
                'work_type': work_type,
                'customer_price': customer_price,
                'area': area,
                'cost': cost,
                'status': 'В обработке',
                'user': current_user['login']
            }

            data['orders'].append(order)
            save_data()
            messagebox.showinfo("Успех", "Заказ создан!")
            create_order_win.destroy()

        create_order_win = tk.Toplevel(root)
        create_order_win.title("Создание заказа")
        create_order_win.geometry("400x200")

        # Подрядчик
        ttk.Label(create_order_win, text="Подрядчик:").grid(row=0, column=0, padx=5, pady=5)
        contractor_var = tk.StringVar()
        contractor_var.set(data['contractors'][0])
        ttk.OptionMenu(create_order_win, contractor_var, *data['contractors']).grid(row=0, column=1, padx=5, pady=5)

        # Материалы (с множественным выбором)
        ttk.Label(create_order_win, text="Материалы:").grid(row=1, column=0, padx=5, pady=5)
        materials_frame = ttk.Frame(create_order_win)
        materials_frame.grid(row=1, column=1, padx=5, pady=5)

        materials_listbox = tk.Listbox(materials_frame, selectmode=tk.MULTIPLE, height=5)
        materials_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(materials_frame, orient="vertical", command=materials_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        materials_listbox.config(yscrollcommand=scrollbar.set)
        for material in data['materials']:
            materials_listbox.insert(tk.END, material)

        # Объект
        ttk.Label(create_order_win, text="Объект:").grid(row=2, column=0, padx=5, pady=5)
        object_var = tk.StringVar()
        object_var.set(data['objects'][0])
        ttk.OptionMenu(create_order_win, object_var, *data['objects']).grid(row=2, column=1, padx=5, pady=5)

        # Тип работы
        ttk.Label(create_order_win, text="Тип работы:").grid(row=3, column=0, padx=5, pady=5)
        work_type_var = tk.StringVar()
        work_type_var.set(data['types_of_work'][0])
        ttk.OptionMenu(create_order_win, work_type_var, *data['types_of_work']).grid(row=3, column=1, padx=5, pady=5)

        # Цена и площадь
        ttk.Label(create_order_win, text="Цена за метр:").grid(row=4, column=0, padx=5, pady=5)
        customer_price_entry = ttk.Entry(create_order_win)
        customer_price_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(create_order_win, text="Площадь (м²):").grid(row=5, column=0, padx=5, pady=5)
        area_entry = ttk.Entry(create_order_win)
        area_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(create_order_win, text="Создать заказ", command=create_order).grid(row=6, columnspan=2, pady=10)

    def view_orders():
        orders_window = tk.Toplevel(root)
        orders_window.title("Заказы")
        orders_window.geometry("400x200")

        tree = ttk.Treeview(orders_window, columns=(
            'Логин', 'Подрядчик', 'Материалы', 'Объект', 'Тип работы',
            'Цена/м²', 'Площадь', 'Стоимость', 'Статус'
        ), show='headings')

        tree.heading('Логин', text='Логин', anchor=tk.W)
        tree.heading('Подрядчик', text='Подрядчик', anchor=tk.W)
        tree.heading('Материалы', text='Материалы', anchor=tk.W)
        tree.heading('Объект', text='Объект', anchor=tk.W)
        tree.heading('Тип работы', text='Тип работы', anchor=tk.W)
        tree.heading('Цена/м²', text='Цена/м²', anchor=tk.W)
        tree.heading('Площадь', text='Площадь', anchor=tk.W)
        tree.heading('Стоимость', text='Стоимость', anchor=tk.W)
        tree.heading('Статус', text='Статус', anchor=tk.W)

        # Настройка ширины столбцов
        tree.column('Логин', width=100, stretch=tk.NO)
        tree.column('Подрядчик', width=150, stretch=tk.NO)
        tree.column('Материалы', width=200, stretch=tk.NO)
        tree.column('Объект', width=120, stretch=tk.NO)
        tree.column('Тип работы', width=180, stretch=tk.NO)
        tree.column('Цена/м²', width=100, stretch=tk.NO)
        tree.column('Площадь', width=80, stretch=tk.NO)
        tree.column('Стоимость', width=120, stretch=tk.NO)
        tree.column('Статус', width=150, stretch=tk.NO)

        tree.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        for order in data['orders']:
            tree.insert('', 'end', values=(
                order['user'],
                order['contractor'],
                ', '.join(order['materials']),
                order['object'],
                order['work_type'],
                order['customer_price'],
                order['area'],
                order['cost'],
                order['status']
            ))

    def edit_order():
        def update_status():
            selected = order_listbox.curselection()
            if not selected:
                return
            order_index = selected[0]
            new_status = status_var.get()
            data['orders'][order_index]['status'] = new_status
            save_data()
            messagebox.showinfo("Успех", "Статус заказа обновлен!")
            edit_win.destroy()

        edit_win = tk.Toplevel(root)
        edit_win.title("Изменение статуса заказа")
        edit_win.geometry("800x400")

        ttk.Label(edit_win, text="Выберите заказ:").pack(pady=5)
        order_listbox = tk.Listbox(edit_win, width=80)
        order_listbox.pack(padx=10, pady=5)

        for idx, order in enumerate(data['orders']):
            order_listbox.insert(tk.END,
                                 f"Заказ {idx}: {order['user']} - {order['contractor']} - {', '.join(order['materials'])}")

        ttk.Label(edit_win, text="Новый статус:").pack(pady=5)
        status_var = tk.StringVar()
        status_var.set(data['order_statuses'][0])
        ttk.OptionMenu(edit_win, status_var, *data['order_statuses']).pack(padx=5, pady=5)

        ttk.Button(edit_win, text="Обновить статус", command=update_status).pack(pady=10)

    def admin_edit_order():
        def save_changes():
            selected = order_listbox.curselection()
            if not selected:
                return
            order_index = selected[0]
            new_order = {
                'contractor': contractor_var.get(),
                'materials': [materials_listbox.get(i) for i in materials_listbox.curselection()],
                'object': object_var.get(),
                'work_type': work_type_var.get(),
                'customer_price': float(customer_price_entry.get()),
                'area': float(area_entry.get()),
                'status': status_var.get()
            }

            # Расчет стоимости
            material_cost = sum(data['materials'][m] for m in new_order['materials'])
            cost = material_cost + work_type_multiplier[new_order['work_type']] * new_order['customer_price'] * \
                   new_order['area']
            new_order['cost'] = cost

            data['orders'][order_index].update(new_order)
            save_data()
            messagebox.showinfo("Успех", "Заказ обновлен!")
            edit_win.destroy()

        edit_win = tk.Toplevel(root)
        edit_win.title("Редактирование заказа (Админ)")
        edit_win.geometry("800x600")

        # Выбор заказа
        ttk.Label(edit_win, text="Выберите заказ:").pack(pady=5)
        order_listbox = tk.Listbox(edit_win, width=80)
        order_listbox.pack(padx=10, pady=5)

        for idx, order in enumerate(data['orders']):
            order_listbox.insert(tk.END,
                                 f"Заказ {idx}: {order['user']} - {order['contractor']} - {', '.join(order['materials'])}")

        # Форма редактирования
        form_frame = ttk.Frame(edit_win)
        form_frame.pack(padx=10, pady=10)

        # Подрядчик
        ttk.Label(form_frame, text="Подрядчик:").grid(row=0, column=0)
        contractor_var = tk.StringVar()
        ttk.OptionMenu(form_frame, contractor_var, data['orders'][0]['contractor'], *data['contractors']).grid(row=0,
                                                                                                               column=1)

        # Материалы
        ttk.Label(form_frame, text="Материалы:").grid(row=1, column=0)
        materials_listbox = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, height=5)
        materials_listbox.grid(row=1, column=1, padx=5)

        for material in data['materials']:
            materials_listbox.insert(tk.END, material)

        # Объект
        ttk.Label(form_frame, text="Объект:").grid(row=2, column=0)
        object_var = tk.StringVar()
        ttk.OptionMenu(form_frame, object_var, data['orders'][0]['object'], *data['objects']).grid(row=2, column=1)

        # Тип работы
        ttk.Label(form_frame, text="Тип работы:").grid(row=3, column=0)
        work_type_var = tk.StringVar()
        ttk.OptionMenu(form_frame, work_type_var, data['orders'][0]['work_type'], *data['types_of_work']).grid(row=3,
                                                                                                               column=1)

        # Цена и площадь
        ttk.Label(form_frame, text="Цена за метр:").grid(row=4, column=0)
        customer_price_entry = ttk.Entry(form_frame)
        customer_price_entry.grid(row=4, column=1)

        ttk.Label(form_frame, text="Площадь (м²):").grid(row=5, column=0)
        area_entry = ttk.Entry(form_frame)
        area_entry.grid(row=5, column=1)

        # Статус
        ttk.Label(form_frame, text="Статус:").grid(row=6, column=0)
        status_var = tk.StringVar()
        ttk.OptionMenu(form_frame, status_var, data['orders'][0]['status'], *data['order_statuses']).grid(row=6,
                                                                                                          column=1)

        ttk.Button(edit_win, text="Сохранить изменения", command=save_changes).pack(pady=10)

    def admin_panel():
        if not current_user or current_user['role'] != 'admin':
            return messagebox.showerror("Ошибка", "Доступ запрещен!")

        admin_win = tk.Toplevel(root)
        admin_win.title("Админ панель")
        admin_win.geometry("400x600")

        def update_list(name, current_list):
            new_values = simpledialog.askstring(
                f"Обновить {name}",
                f"Введите новые значения через запятую\n(Текущие: {', '.join(current_list)})",
                initialvalue=','.join(current_list)
            )
            if new_values:
                if name == 'materials':
                    new_materials = {}
                    for item in new_values.split(','):
                        mat, price = item.strip().split(':')
                        new_materials[mat] = float(price)
                    data[name] = new_materials
                else:
                    data[name] = [v.strip() for v in new_values.split(',')]
                save_data()
                messagebox.showinfo("Успех", f"{name} обновлены!")

        ttk.Button(admin_win, text="Обновить подрядчиков",
                   command=lambda: update_list('contractors', data['contractors'])).pack(pady=5)
        ttk.Button(admin_win, text="Обновить материалы",
                   command=lambda: update_list('materials', [f"{k}:{v}" for k, v in data['materials'].items()])).pack(
            pady=5)
        ttk.Button(admin_win, text="Обновить объекты", command=lambda: update_list('objects', data['objects'])).pack(
            pady=5)
        ttk.Button(admin_win, text="Обновить типы работ",
                   command=lambda: update_list('types_of_work', data['types_of_work'])).pack(pady=5)
        ttk.Button(admin_win, text="Изменить заказы", command=admin_edit_order).pack(pady=5)

    def update_main_buttons():
        if current_user:
            login_button.pack_forget()
            register_button.pack_forget()
            logout_button.pack(side=tk.TOP, pady=5)
            logout_button.config(state=tk.NORMAL)
        else:
            login_button.pack(side=tk.TOP, pady=5)
            register_button.pack(side=tk.TOP, pady=5)
            logout_button.pack_forget()
            logout_button.config(state=tk.DISABLED)

    # Основное окно
    root = tk.Tk()
    root.title("Расчет стоимости ремонтных работ")
    root.geometry("400x400")

    login_button = ttk.Button(root, text="Вход", command=login_window)
    register_button = ttk.Button(root, text="Регистрация", command=register_user)
    logout_button = ttk.Button(root, text="Выйти", command=logout, state=tk.DISABLED)

    login_button.pack(side=tk.TOP, pady=5)
    register_button.pack(side=tk.TOP, pady=5)
    logout_button.pack(side=tk.TOP, pady=5)

    ttk.Button(root, text="Создать заказ", command=create_order_window).pack(pady=5)
    ttk.Button(root, text="Просмотреть заказы", command=view_orders).pack(pady=5)
    ttk.Button(root, text="Изменить статус заказа", command=edit_order).pack(pady=5)
    ttk.Button(root, text="Админ панель", command=admin_panel).pack(pady=5)

    update_main_buttons()
    root.mainloop()


if __name__ == "__main__":
    show_file_chooser()