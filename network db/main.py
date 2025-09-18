import sqlite3

conn = sqlite3.connect('social_network.db')
cursor = conn.cursor()

# Создаем таблицу Users (если не существует)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
);
""")

# Создаем таблицу Posts (если не существует)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    post_content TEXT,
    likes_count INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
);
""")

# Проверяем, есть ли данные в Users — если нет, вставим тестовые
cursor.execute("SELECT COUNT(*) FROM Users;")
if cursor.fetchone()[0] == 0:
    users = [
        (1, 'RM'),
        (2, 'Jin'),
        (3, 'SUGA'),
        (4, 'j-hope'),
        (5, 'Jimin'),
        (6, 'V'),
        (7, 'Jungkook')
    ]
    cursor.executemany("INSERT INTO Users (user_id, username) VALUES (?, ?);", users)

# Проверяем, есть ли данные в Posts — если нет, вставим тестовые
cursor.execute("SELECT COUNT(*) FROM Posts;")
if cursor.fetchone()[0] == 0:
    posts = [
        (1, 1, 'Post by RM', 100),
        (2, 1, 'Another post by RM', 50),
        (3, 3, 'Post by SUGA', 200),
        (4, 5, 'Post by Jimin', 150),
        (5, 7, 'Post by Jungkook', 120),
    ]
    cursor.executemany("INSERT INTO Posts (post_id, user_id, post_content, likes_count) VALUES (?, ?, ?, ?);", posts)

conn.commit()

# Создаем таблицу UserLikesSummary (если не существует)
cursor.execute("""
CREATE TABLE IF NOT EXISTS UserLikesSummary (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    total_likes INTEGER
);
""")

# Очищаем таблицу перед вставкой новых данных
cursor.execute("DELETE FROM UserLikesSummary;")

# Вставляем агрегированные данные
cursor.execute("""
INSERT INTO UserLikesSummary (user_id, username, total_likes)
SELECT
    u.user_id,
    u.username,
    COALESCE(SUM(p.likes_count), 0) AS total_likes
FROM
    Users u
LEFT JOIN
    Posts p ON u.user_id = p.user_id
GROUP BY
    u.user_id,
    u.username;
""")

conn.commit()

# Выводим содержимое UserLikesSummary
cursor.execute("SELECT * FROM UserLikesSummary ORDER BY total_likes DESC;")
rows = cursor.fetchall()

print("UserLikesSummary:")
for row in rows:
    print(row)

conn.close()
