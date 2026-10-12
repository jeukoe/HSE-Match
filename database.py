import sqlite3


def create_database():
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            skills TEXT,
            interests TEXT,
            course TEXT,
            institute TEXT,
            role TEXT,
            goal TEXT,
            free_time TEXT,
            about TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(profiles)")
    columns = [row[1] for row in cursor.fetchall()]

    new_columns = {
        "skills": "TEXT",
        "interests": "TEXT",
        "course": "TEXT",
        "institute": "TEXT",
        "role": "TEXT",
        "goal": "TEXT",
        "free_time": "TEXT",
        "about": "TEXT"
    }

    for column, column_type in new_columns.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE profiles ADD COLUMN {column} {column_type}"
            )

    connection.commit()
    connection.close()


def save_profile(
    user_id, name, interests, course, institute,
    skills, role, goal, free_time, about
):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO profiles (
            user_id, name, interests, course, institute,
            skills, role, goal, free_time, about
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, name, interests, course, institute,
        skills, role, goal, free_time, about
    ))

    connection.commit()
    connection.close()


def get_profile(user_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            name, interests, course, institute, skills,
            role, goal, free_time, about
        FROM profiles
        WHERE user_id = ?
    """, (user_id,))

    profile = cursor.fetchone()
    connection.close()

    return profile


def update_name(user_id, new_name):
    update_field(user_id, "name", new_name)


def update_skills(user_id, new_skills):
    update_field(user_id, "skills", new_skills)


def update_interests(user_id, new_interests):
    update_field(user_id, "interests", new_interests)


def update_course(user_id, new_course):
    update_field(user_id, "course", new_course)


def update_institute(user_id, new_institute):
    update_field(user_id, "institute", new_institute)


def update_role(user_id, new_role):
    update_field(user_id, "role", new_role)


def update_goal(user_id, new_goal):
    update_field(user_id, "goal", new_goal)


def update_free_time(user_id, new_free_time):
    update_field(user_id, "free_time", new_free_time)


def update_about(user_id, new_about):
    update_field(user_id, "about", new_about)


def update_field(user_id, field, value):
    allowed_fields = {
        "name", "skills", "interests", "course", "institute",
        "role", "goal", "free_time", "about"
    }

    if field not in allowed_fields:
        raise ValueError("Неизвестное поле анкеты")

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute(
        f"UPDATE profiles SET {field} = ? WHERE user_id = ?",
        (value, user_id)
    )

    connection.commit()
    connection.close()

