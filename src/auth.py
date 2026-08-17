"""Authentication and role-based access for NeuroScan Nepal."""

from __future__ import annotations

import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "neuroscan.db"

ROLES = ("radiologist", "doctor", "patient")
ROLE_LABELS = {
    "radiologist": "Radiologist",
    "doctor": "Doctor",
    "patient": "Patient",
}

JWT_SECRET = os.getenv("NEUROSCAN_JWT_SECRET", "neuroscan-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('radiologist', 'doctor', 'patient')),
                patient_unique_id TEXT UNIQUE,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
            CREATE INDEX IF NOT EXISTS idx_users_patient_id ON users(patient_unique_id);
            """
        )
        conn.commit()


def _next_patient_id(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM users WHERE role = 'patient'"
    ).fetchone()
    seq = int(row["cnt"]) + 1
    return f"NSN-PAT-{seq:06d}"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _row_to_user(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "patient_unique_id": row["patient_unique_id"],
        "created_at": row["created_at"],
    }


def create_user(
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> Dict[str, Any]:
    if role not in ROLES:
        raise ValueError(f"Invalid role: {role}")

    user_id = secrets.token_hex(16)
    patient_unique_id = None
    if role == "patient":
        with _connect() as conn:
            patient_unique_id = _next_patient_id(conn)
            conn.execute(
                """
                INSERT INTO users (id, email, password_hash, full_name, role, patient_unique_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email.lower().strip(),
                    hash_password(password),
                    full_name.strip(),
                    role,
                    patient_unique_id,
                    time.time(),
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return _row_to_user(row)

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (id, email, password_hash, full_name, role, patient_unique_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email.lower().strip(),
                hash_password(password),
                full_name.strip(),
                role,
                None,
                time.time(),
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return _row_to_user(row) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row) if row else None


def get_user_by_patient_id(patient_unique_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE patient_unique_id = ?",
            (patient_unique_id.strip().upper(),),
        ).fetchone()
        return _row_to_user(row) if row else None


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            return None
        return _row_to_user(row)


def list_patients() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, email, full_name, role, patient_unique_id, created_at
            FROM users WHERE role = 'patient'
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [_row_to_user(r) for r in rows]


def create_access_token(user: Dict[str, Any]) -> str:
    payload = {
        "sub": user["id"],
        "role": user["role"],
        "email": user["email"],
        "exp": time.time() + JWT_EXPIRE_HOURS * 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    payload = decode_token(credentials.credentials)
    user = get_user_by_id(payload.get("sub", ""))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_roles(*allowed: str):
    def checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(allowed)}",
            )
        return user

    return checker


def seed_demo_users() -> None:
    """Create demo accounts if the database is empty."""
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
        if count > 0:
            return

    demos = [
        ("radiologist@neuroscan.np", "radiologist123", "Kishor Phuyal", "radiologist"),
        ("doctor@neuroscan.np", "doctor123", "Dr. Bikram Prasad Gajurel", "doctor"),
        ("patient@neuroscan.np", "patient123", "Ram Bahadur Thapa", "patient"),
    ]
    for email, password, name, role in demos:
        try:
            create_user(email, password, name, role)
        except sqlite3.IntegrityError:
            pass
