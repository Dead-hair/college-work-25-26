import sqlite3
import os

db_file = 'company.db'

# Удаляем старую базу, если она есть
if os.path.exists(db_file):
    os.remove(db_file)

# Подключаемся к базе данных
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript("""
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department TEXT
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    employee_id INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
""")

# Вставляем данные в таблицу сотрудников — теперь больше сотрудников
cursor.executemany("""
INSERT INTO employees (employee_id, employee_name, department) VALUES (?, ?, ?);
""", [
    (1, 'Иван Иванов', 'Отдел разработки'),
    (2, 'Мария Петрова', 'Отдел маркетинга'),
    (3, 'Петр Сидоров', 'Отдел разработки'),
    (4, 'Анна Смирнова', 'Отдел продаж'),
    (5, 'Алексей Козлов', 'Отдел разработки'),
    (6, 'Екатерина Морозова', 'Отдел маркетинга'),
    (7, 'Дмитрий Соколов', 'Отдел продаж')
])

# Вставляем данные в таблицу проектов
cursor.executemany("""
INSERT INTO projects (project_id, project_name, employee_id) VALUES (?, ?, ?);
""", [
    (1, 'Проект А', 1),
    (2, 'Проект Б', 1),
    (3, 'Проект В', 3),
    (4, 'Проект Г', None)  # проект без сотрудника
])

conn.commit()

# Запрос: вывести сотрудников, которые не работают ни над одним проектом
query = """
SELECT e.employee_id, e.employee_name, e.department
FROM employees e
LEFT JOIN projects p ON e.employee_id = p.employee_id
WHERE p.project_id IS NULL
ORDER BY e.employee_id;
"""

cursor.execute(query)
rows = cursor.fetchall()

print("Сотрудники, которые не работают ни над одним проектом:\n")
for employee_id, name, department in rows:
    print(f"ID: {employee_id}, Имя: {name}, Отдел: {department}")

conn.close()
