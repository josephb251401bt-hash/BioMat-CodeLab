"""Shared SQLite-backed progress storage for BioMat CodeLab.

For local use, progress is stored in student_progress.db beside app.py.
For durable multi-user cloud deployment, configure BIOMAT_DB_PATH to a
persistent mounted volume or replace this adapter with a hosted database.
"""
from pathlib import Path
import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("BIOMAT_DB_PATH", str(BASE_DIR / "student_progress.db")))
MISSIONS = ("biotechnology", "materials_science", "biomaterials")

@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            mission TEXT NOT NULL,
            task_id TEXT NOT NULL,
            xp INTEGER NOT NULL CHECK (xp >= 0),
            completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, mission, task_id),
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_completions_student ON completions(student_id)")

def register_student(student_id: str, display_name: str):
    student_id = student_id.strip().lower()
    display_name = display_name.strip()
    if not student_id or not display_name:
        raise ValueError("Enter both a student username/ID and display name.")
    if len(student_id) > 40 or len(display_name) > 80:
        raise ValueError("Student ID must be <=40 characters and name <=80 characters.")
    init_db()
    with connection() as conn:
        conn.execute("""INSERT INTO students(student_id, display_name)
            VALUES(?, ?) ON CONFLICT(student_id) DO UPDATE SET
            display_name=excluded.display_name, last_seen=CURRENT_TIMESTAMP""",
            (student_id, display_name))
    return student_id

def award_xp(student_id: str, mission: str, task_id: str, xp: int) -> bool:
    """Insert a completion once. Returns True only when XP was newly awarded."""
    if mission not in MISSIONS:
        raise ValueError(f"Unknown mission: {mission}")
    init_db()
    with connection() as conn:
        cur = conn.execute("""INSERT OR IGNORE INTO completions
            (student_id, mission, task_id, xp) VALUES (?, ?, ?, ?)""",
            (student_id, mission, str(task_id), int(xp)))
        return cur.rowcount == 1

def get_progress(student_id: str):
    init_db()
    with connection() as conn:
        rows = conn.execute("""SELECT mission, task_id, xp, completed_at
            FROM completions WHERE student_id=? ORDER BY completed_at""", (student_id,)).fetchall()
    tasks = {m: set() for m in MISSIONS}
    mission_xp = {m: 0 for m in MISSIONS}
    for row in rows:
        tasks[row["mission"]].add(row["task_id"])
        mission_xp[row["mission"]] += row["xp"]
    return {
        "total_xp": sum(mission_xp.values()),
        "total_completed": sum(len(v) for v in tasks.values()),
        "mission_xp": mission_xp,
        "tasks": tasks,
    }

def get_leaderboard(limit=20):
    init_db()
    with connection() as conn:
        rows = conn.execute("""SELECT s.display_name, s.student_id,
            COALESCE(SUM(c.xp),0) AS total_xp,
            COUNT(c.id) AS completed_tasks
            FROM students s LEFT JOIN completions c ON s.student_id=c.student_id
            GROUP BY s.student_id, s.display_name
            ORDER BY total_xp DESC, completed_tasks DESC, s.display_name ASC
            LIMIT ?""", (int(limit),)).fetchall()
    return [dict(r) for r in rows]

def clear_student_progress(student_id: str):
    init_db()
    with connection() as conn:
        conn.execute("DELETE FROM completions WHERE student_id=?", (student_id,))
