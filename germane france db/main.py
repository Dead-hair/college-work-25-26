import sqlite3

conn = sqlite3.connect('germane_france.db')
cursor = conn.cursor()

# Создаем таблицы Customers и Employees
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Country TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    EmployeeID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Country TEXT
);
""")

# Добавляем данные, если таблицы пусты
cursor.execute("SELECT COUNT(*) FROM Customers;")
if cursor.fetchone()[0] == 0:
    customers = [
        (1, 'Anna Schmidt', 'Berlin', 'Germany'),
        (2, 'Jean Dupont', 'Paris', 'France'),
        (3, 'Maria Rossi', 'Rome', 'Italy'),
        (4, 'Sophie Müller', 'Hamburg', 'Germany'),
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?);", customers)

cursor.execute("SELECT COUNT(*) FROM Employees;")
if cursor.fetchone()[0] == 0:
    employees = [
        (1, 'Hans Müller', 'Munich', 'Germany'),
        (2, 'Claire Dubois', 'Lyon', 'France'),
        (3, 'John Smith', 'London', 'UK'),
        (4, 'Pierre Martin', 'Marseille', 'France'),
    ]
    cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?);", employees)

conn.commit()

# Создаем таблицу PeopleInGermanyFrance
cursor.execute("""
CREATE TABLE IF NOT EXISTS PeopleInGermanyFrance (
    PersonID INTEGER,
    Name TEXT,
    City TEXT,
    Country TEXT,
    Role TEXT
);
""")

# Очищаем таблицу перед вставкой новых данных
cursor.execute("DELETE FROM PeopleInGermanyFrance;")

# Вставляем данные с ролью
cursor.execute("""
INSERT INTO PeopleInGermanyFrance (PersonID, Name, City, Country, Role)
SELECT CustomerID, Name, City, Country, 'Customer' FROM Customers WHERE Country IN ('Germany', 'France')
UNION ALL
SELECT EmployeeID, Name, City, Country, 'Employee' FROM Employees WHERE Country IN ('Germany', 'France');
""")

conn.commit()

print("Данные добавлены в таблицу PeopleInGermanyFrance.")

conn.close()
