import sqlite3

conn = sqlite3.connect('people_phones.db')  # файл базы
cursor = conn.cursor()

# Создаем таблицы Customers, Employees, Suppliers (если их нет)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    Name TEXT,
    Phone TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    Name TEXT,
    Phone TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Suppliers (
    Name TEXT,
    Phone TEXT
);
""")

# Вставляем данные, если таблицы пусты
cursor.execute("SELECT COUNT(*) FROM Customers;")
if cursor.fetchone()[0] == 0:
    customers = [
        ('Anna Schmidt', '123-456-789'),
        ('Jean Dupont', None),
        ('Maria Rossi', '555-555-555'),
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?, ?);", customers)

cursor.execute("SELECT COUNT(*) FROM Employees;")
if cursor.fetchone()[0] == 0:
    employees = [
        ('Hans Müller', '123-456-789'),
        ('Claire Dubois', None),
        ('John Smith', '999-999-999'),
    ]
    cursor.executemany("INSERT INTO Employees VALUES (?, ?);", employees)

cursor.execute("SELECT COUNT(*) FROM Suppliers;")
if cursor.fetchone()[0] == 0:
    suppliers = [
        ('Pierre Martin', '555-555-555'),
        ('Sophie Müller', None),
        ('Anna Schmidt', '123-456-789'),
    ]
    cursor.executemany("INSERT INTO Suppliers VALUES (?, ?);", suppliers)

conn.commit()

# Создаем новую таблицу для объединенного списка
cursor.execute("""
CREATE TABLE IF NOT EXISTS AllPeoplePhones (
    Name TEXT,
    Phone TEXT
);
""")

# Очищаем таблицу перед вставкой
cursor.execute("DELETE FROM AllPeoplePhones;")

# Вставляем уникальные данные с заменой NULL на 'Номер не указан'
cursor.execute("""
INSERT INTO AllPeoplePhones (Name, Phone)
SELECT DISTINCT Name, COALESCE(Phone, 'Номер не указан') AS Phone FROM Customers
UNION
SELECT DISTINCT Name, COALESCE(Phone, 'Номер не указан') AS Phone FROM Employees
UNION
SELECT DISTINCT Name, COALESCE(Phone, 'Номер не указан') AS Phone FROM Suppliers;
""")

conn.commit()

print("Данные успешно сохранены в таблице AllPeoplePhones.")

conn.close()
