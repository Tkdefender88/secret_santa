"""Database setup and models for secret santa."""

import sqlite3
import os
from typing import List, Dict


DATABASE_PATH = 'santa.db'


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema."""
    if os.path.exists(DATABASE_PATH):
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # People table
    cursor.execute('''
        CREATE TABLE people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL
        )
    ''')
    
    # Assignments table
    cursor.execute('''
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            giver_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            FOREIGN KEY (giver_id) REFERENCES people(id),
            FOREIGN KEY (recipient_id) REFERENCES people(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def add_person(name: str, surname: str) -> int:
    """Add person to database. Returns person ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO people (name, surname) VALUES (?, ?)', (name, surname))
    conn.commit()
    person_id = cursor.lastrowid
    conn.close()
    return person_id


def get_all_people() -> List[Dict]:
    """Get all people from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, surname FROM people')
    people = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return people


def clear_people():
    """Delete all people from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM people')
    conn.commit()
    conn.close()


def save_assignments(assignments: Dict[int, int]):
    """Save assignments to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear old assignments
    cursor.execute('DELETE FROM assignments')
    
    # Insert new assignments
    for giver_id, recipient_id in assignments.items():
        cursor.execute(
            'INSERT INTO assignments (giver_id, recipient_id) VALUES (?, ?)',
            (giver_id, recipient_id)
        )
    
    conn.commit()
    conn.close()


def get_assignment(giver_id: int) -> Dict:
    """Get assignment for a person."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, p.surname 
        FROM people p
        JOIN assignments a ON p.id = a.recipient_id
        WHERE a.giver_id = ?
    ''', (giver_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_all_assignments() -> Dict[int, int]:
    """Get all assignments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT giver_id, recipient_id FROM assignments')
    assignments = {row['giver_id']: row['recipient_id'] for row in cursor.fetchall()}
    conn.close()
    return assignments
