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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def delete_profile(user_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
    connection.commit()
    connection.close()

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

def get_candidates(user_id):
    """user_id всех, у кого есть анкета и нет pending-приглашения от user_id."""
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.user_id
        FROM profiles p
        WHERE p.user_id != ?
          AND p.user_id NOT IN (
              SELECT to_user_id FROM invitations
              WHERE from_user_id = ? AND status = 'pending'
          )
    """, (user_id, user_id))
    result = [row[0] for row in cursor.fetchall()]
    connection.close()
    return result


def create_invitation(from_user_id, to_user_id):
    """
    Создаёт приглашение со статусом 'pending'.
    Возвращает id приглашения или None, если pending уже есть.
    """
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id FROM invitations
        WHERE from_user_id = ? AND to_user_id = ? AND status = 'pending'
    """, (from_user_id, to_user_id))
    if cursor.fetchone() is not None:
        connection.close()
        return None
    cursor.execute("""
        INSERT INTO invitations (from_user_id, to_user_id, status)
        VALUES (?, ?, 'pending')
    """, (from_user_id, to_user_id))
    invitation_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return invitation_id


def get_invitation(invitation_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT from_user_id, to_user_id, status
        FROM invitations WHERE id = ?
    """, (invitation_id,))
    invitation = cursor.fetchone()
    connection.close()
    return invitation


def update_invitation_status(invitation_id, status):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE invitations SET status = ? WHERE id = ?",
        (status, invitation_id)
    )
    connection.commit()
    connection.close()


def get_pending_invitations_for(to_user_id):
    """Список (invitation_id, from_user_id) входящих pending-приглашений."""
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, from_user_id FROM invitations
        WHERE to_user_id = ? AND status = 'pending'
        ORDER BY id DESC
    """, (to_user_id,))
    result = cursor.fetchall()
    connection.close()
    return result
