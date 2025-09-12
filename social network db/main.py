import sqlite3
import bcrypt
from cryptography.fernet import Fernet

# Генерация ключа шифрования (сохраните в безопасном месте!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Подключение к базе данных SQLite
conn = sqlite3.connect('social_network.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    is_group BOOLEAN
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_members (
    chat_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY(chat_id, user_id),
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    sender_id INTEGER,
    encrypted_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
)
''')

conn.commit()

# Функция для регистрации пользователя с хешированием пароля
def register_user(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"Пользователь {username} зарегистрирован.")
    except sqlite3.IntegrityError:
        print(f"Имя пользователя {username} уже занято.")

# Функция аутентификации пользователя
def authenticate_user(username, password):
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        print("Аутентификация успешна.")
        return True
    print("Неверный логин или пароль.")
    return False

# Создание поста
def create_post(user_id, content):
    cursor.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()

# Добавление комментария к посту
def add_comment(post_id, user_id, content):
    cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)", (post_id, user_id, content))
    conn.commit()

# Создание чата (личный или групповой)
def create_chat(name, is_group):
    cursor.execute("INSERT INTO chats (name, is_group) VALUES (?, ?)", (name, is_group))
    conn.commit()
    return cursor.lastrowid

# Добавление пользователя в чат
def add_member_to_chat(chat_id, user_id):
    cursor.execute("INSERT OR IGNORE INTO chat_members (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
    conn.commit()

# Отправка зашифрованного сообщения
def send_message(chat_id, sender_id, message):
    encrypted_message = cipher.encrypt(message.encode('utf-8'))
    cursor.execute("INSERT INTO messages (chat_id, sender_id, encrypted_message) VALUES (?, ?, ?)", 
                   (chat_id, sender_id, encrypted_message.decode('utf-8')))
    conn.commit()

# Чтение сообщений из чата (расшифровка)
def read_messages(chat_id):
    cursor.execute("SELECT sender_id, encrypted_message, created_at FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
    messages = cursor.fetchall()
    for sender_id, encrypted_msg, created_at in messages:
        decrypted_msg = cipher.decrypt(encrypted_msg.encode('utf-8')).decode('utf-8')
        print(f"[{created_at}] User {sender_id}: {decrypted_msg}")

# Получение id пользователя по имени
def get_user_id(username):
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


if __name__ == "__main__":
    # Регистрация пользователей Alice и Bob
    register_user("alice", "password123")
    register_user("bob", "securepass")

    # Предполагаем, что ID пользователей Alice = 1, Bob = 2
    create_post(1, "Привет, это мой первый пост!")
    add_comment(1, 2, "Отличный пост, Alice!")

    chat_id = create_chat("Alice & Bob", False)
    add_member_to_chat(chat_id, 1)
    add_member_to_chat(chat_id, 2)
    send_message(chat_id, 1, "Привет, Bob!")
    send_message(chat_id, 2, "Привет, Alice! Как дела?")

    print("Сообщения в чате Alice и Bob:")
    read_messages(chat_id)

    # --- Добавляем чат Хисын и Сону ---

    register_user("Хисын", "pass1")
    register_user("Сону", "pass2")

    hisin_id = get_user_id("Хисын")
    sonu_id = get_user_id("Сону")

    chat_id2 = create_chat("Чат Хисын и Сону", False)
    add_member_to_chat(chat_id2, hisin_id)
    add_member_to_chat(chat_id2, sonu_id)

    send_message(chat_id2, hisin_id, "Привет, Сону! Когда начнется тренировка?")
    send_message(chat_id2, sonu_id, "Привет, Хисын! Думаю, в 18:00.")

    print("\nСообщения в чате Хисын и Сону:")
    read_messages(chat_id2)

    conn.close()
