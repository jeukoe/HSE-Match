import re
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            UNIQUE(requester_id, target_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_usernames (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    """)
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

# ---------------------------------------------------------------------------
# Поиск участников и фильтрация
# ---------------------------------------------------------------------------

# Поля, по которым можно искать. "all" - сразу по всем текстовым полям.
SEARCH_FIELDS = {
    "skills": ("skills",),
    "interests": ("interests",),
    "role": ("role",),
    "goal": ("goal",),
    "all": ("skills", "interests", "role", "goal", "course", "about"),
}

_PROFILE_COLUMNS = (
    "user_id", "name", "interests", "course", "institute",
    "skills", "role", "goal", "free_time", "about"
)


def split_terms(text):
    """'Python, C++; дизайн' -> ['python', 'c++', 'дизайн'] (в нижнем регистре)."""
    if not text:
        return []
    parts = re.split(r"[,;\n]+", text)
    terms = []
    for part in parts:
        part = part.strip().casefold()
        if part and part not in terms:
            terms.append(part)
    return terms


def _term_in_text(term, text):
    # Совпадение с начала слова: "pyth" найдёт "Python", но "ython" - нет.
    pattern = r"(?<!\w)" + re.escape(term)
    return re.search(pattern, text) is not None


def search_profiles(exclude_user_id, query="", search_field="all"):
    """
    Ищет участников, кроме exclude_user_id.
    query - термины через запятую. Пустой query = вернуть всех.
    Сортировка: сначала те, у кого больше совпавших терминов.
    Возвращает список словарей (ключи из _PROFILE_COLUMNS + matched, total).
    """
    if search_field not in SEARCH_FIELDS:
        raise ValueError("Неизвестное поле поиска")

    terms = split_terms(query)

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT {', '.join(_PROFILE_COLUMNS)} FROM profiles "
        "WHERE user_id != ?",
        (exclude_user_id,)
    )
    rows = cursor.fetchall()
    connection.close()

    results = []
    for row in rows:
        profile = dict(zip(_PROFILE_COLUMNS, row))

        # Фильтрацию делаем в Python: SQLite LOWER()/LIKE не умеет
        # регистронезависимо работать с кириллицей.
        haystack = " ".join(
            (profile[f] or "") for f in SEARCH_FIELDS[search_field]
        ).casefold()

        matched = [t for t in terms if _term_in_text(t, haystack)]

        if terms and not matched:
            continue

        profile["matched"] = len(matched)
        profile["total"] = len(terms)
        results.append(profile)

    results.sort(key=lambda p: (-p["matched"], (p["name"] or "").casefold()))
    return results


def get_popular_values(field, limit=8, exclude_user_id=None):
    """Самые частые значения поля (навыки, интересы...) - для подсказок."""
    if field not in ("skills", "interests", "role", "goal"):
        raise ValueError("Неизвестное поле")

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT user_id, {field} FROM profiles")
    rows = cursor.fetchall()
    connection.close()

    counts = {}
    shown = {}
    for user_id, value in rows:
        if exclude_user_id is not None and user_id == exclude_user_id:
            continue
        for term in split_terms(value):
            counts[term] = counts.get(term, 0) + 1
            shown.setdefault(term, term)

    top = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:limit]
    return [(shown[t], n) for t, n in top]
def save_telegram_username(user_id, username):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO telegram_usernames (user_id, username)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET username = excluded.username
    """, (user_id, username))

    connection.commit()
    connection.close()


def get_telegram_username(user_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT username FROM telegram_usernames WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    connection.close()

    return result[0] if result else None


def create_contact_request(requester_id, target_id):
    if requester_id == target_id:
        return False

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status FROM contact_requests
        WHERE requester_id = ? AND target_id = ?
    """, (requester_id, target_id))

    existing = cursor.fetchone()

    if existing and existing[0] in ("pending", "accepted"):
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO contact_requests
            (requester_id, target_id, status)
        VALUES (?, ?, 'pending')
        ON CONFLICT(requester_id, target_id)
        DO UPDATE SET status = 'pending'
    """, (requester_id, target_id))

    connection.commit()
    connection.close()
    return True


def get_contact_request(requester_id, target_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status FROM contact_requests
        WHERE requester_id = ? AND target_id = ?
    """, (requester_id, target_id))

    result = cursor.fetchone()
    connection.close()

    return result[0] if result else None


def update_contact_request(requester_id, target_id, status):
    if status not in ("accepted", "rejected"):
        raise ValueError("Недопустимый статус запроса")

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE contact_requests
        SET status = ?
        WHERE requester_id = ?
          AND target_id = ?
          AND status = 'pending'
    """, (status, requester_id, target_id))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated
def get_accepted_contact_partners(user_id):
    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT requester_id, target_id
        FROM contact_requests
        WHERE status = 'accepted'
          AND (requester_id = ? OR target_id = ?)
    """, (user_id, user_id))

    rows = cursor.fetchall()
    connection.close()

    partners = []

    for requester_id, target_id in rows:
        partner_id = (
            target_id if requester_id == user_id
            else requester_id
        )
        partners.append(partner_id)

    return partners
