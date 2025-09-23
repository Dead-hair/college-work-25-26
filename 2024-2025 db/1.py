import sqlite3

# === Подключение к SQLite ===
conn = sqlite3.connect('customers.db')  # создаст файл customers.db
cursor = conn.cursor()

# === Удалим таблицы, если они уже существуют (для чистого запуска) ===
cursor.execute('DROP TABLE IF EXISTS Customers2024')
cursor.execute('DROP TABLE IF EXISTS Customers2025')
cursor.execute('DROP TABLE IF EXISTS OnlyIn2024')
cursor.execute('DROP TABLE IF EXISTS OnlyIn2025')

# === Создание таблиц ===
cursor.execute('''
CREATE TABLE Customers2024 (
    CustomerID INTEGER,
    CustomerName TEXT
)
''')

cursor.execute('''
CREATE TABLE Customers2025 (
    CustomerID INTEGER,
    CustomerName TEXT
)
''')

# === Вставка данных ===
data_2024 = [
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Charlie'),
    (4, 'Diana')
]

data_2025 = [
    (3, 'Charlie'),
    (4, 'Diana'),
    (5, 'Eve'),
    (6, 'Frank')
]

cursor.executemany('INSERT INTO Customers2024 VALUES (?, ?)', data_2024)
cursor.executemany('INSERT INTO Customers2025 VALUES (?, ?)', data_2025)

# === Сохраняем результаты EXCEPT в новые таблицы ===

# 1. Клиенты, которые были только в 2024 году
cursor.execute('''
CREATE TABLE OnlyIn2024 AS
SELECT CustomerID, CustomerName
FROM Customers2024
EXCEPT
SELECT CustomerID, CustomerName
FROM Customers2025
''')

# 2. Клиенты, которые появились только в 2025 году
cursor.execute('''
CREATE TABLE OnlyIn2025 AS
SELECT CustomerID, CustomerName
FROM Customers2025
EXCEPT
SELECT CustomerID, CustomerName
FROM Customers2024
''')

# === Подтверждение изменений и закрытие соединения ===
conn.commit()
conn.close()
