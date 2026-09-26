import sqlite3

def create_database():
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            language TEXT,
            interests TEXT,
            course TEXT,
            institute TEXT
        )
    """)
    connection.commit()
    connection.close()

def save_profile(user_id, name, language, interests, course, institute):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO profiles
        (user_id, name, language, interests, course, institute)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, language, interests, course, institute))
    connection.commit()
    connection.close()


def get_profile(user_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT name, language, interests, course, institute
        FROM profiles
        WHERE user_id = ?
    """, (user_id,))
    profile = cursor.fetchone()
    connection.close()
    return profile