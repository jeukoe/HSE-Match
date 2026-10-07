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

def update_name(user_id, new_name):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE profiles
        SET name = ?
        WHERE user_id = ?
    """, (new_name, user_id))
    connection.commit()
    connection.close()

def update_language(user_id, new_language):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE profiles
        SET language = ?
        WHERE user_id = ?
    """, (new_language, user_id))
    connection.commit()
    connection.close()

def update_interests(user_id, new_interests):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE profiles
        SET interests = ?
        WHERE user_id = ?
    """, (new_interests, user_id))
    connection.commit()
    connection.close()

def update_course(user_id, new_course):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE profiles
        SET course = ?
        WHERE user_id = ?
    """, (new_course, user_id))
    connection.commit()
    connection.close()

def update_institute(user_id, new_institute):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE profiles
        SET institute = ?
        WHERE user_id = ?
    """, (new_institute, user_id))
    connection.commit()
    connection.close()