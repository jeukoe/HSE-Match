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
            institute TEXT,
            skills TEXT,
            role TEXT,
            goal TEXT,
            free_time TEXT,
            about TEXT
        )
    """)
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(profiles)").fetchall()]
    new_columns = {
        "language": "TEXT", "skills": "TEXT", "interests": "TEXT",
        "course": "TEXT", "institute": "TEXT", "role": "TEXT",
        "goal": "TEXT", "free_time": "TEXT", "about": "TEXT"
    }
    for column, column_type in new_columns.items():
        if column not in columns:
            cursor.execute(f"ALTER TABLE profiles ADD COLUMN {column} {column_type}")
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
        FROM profiles WHERE user_id = ?
    """, (user_id,))
    profile = cursor.fetchone()
    connection.close()
    return profile


def update_field(user_id, field, value):
    allowed_fields = {"name", "language", "skills", "interests", "course", "institute", "role", "goal", "free_time", "about"}
    if field not in allowed_fields:
        raise ValueError("Неизвестное поле анкеты")
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute(f"UPDATE profiles SET {field} = ? WHERE user_id = ?", (value, user_id))
    connection.commit()
    connection.close()


def update_name(user_id, value): update_field(user_id, "name", value)
def update_language(user_id, value): update_field(user_id, "language", value)
def update_skills(user_id, value): update_field(user_id, "skills", value)
def update_interests(user_id, value): update_field(user_id, "interests", value)
def update_course(user_id, value): update_field(user_id, "course", value)
def update_institute(user_id, value): update_field(user_id, "institute", value)
def update_role(user_id, value): update_field(user_id, "role", value)
def update_goal(user_id, value): update_field(user_id, "goal", value)
def update_free_time(user_id, value): update_field(user_id, "free_time", value)
def update_about(user_id, value): update_field(user_id, "about", value)

