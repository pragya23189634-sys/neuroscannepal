"""Tests for authentication helpers."""

from __future__ import annotations

import auth


def test_hash_and_verify_password():
    hashed = auth.hash_password("secret123")
    assert auth.verify_password("secret123", hashed)
    assert not auth.verify_password("wrong", hashed)


def test_create_user_and_authenticate(tmp_path, monkeypatch):
    db_path = tmp_path / "test_auth.db"
    monkeypatch.setattr(auth, "DB_PATH", db_path)
    auth.init_db()

    user = auth.create_user(
        "test.radiologist@neuroscan.np",
        "password123",
        "Test Radiologist",
        "radiologist",
    )
    assert user["email"] == "test.radiologist@neuroscan.np"
    assert user["role"] == "radiologist"
    assert user["patient_unique_id"] is None

    authed = auth.authenticate_user("test.radiologist@neuroscan.np", "password123")
    assert authed is not None
    assert authed["id"] == user["id"]
    assert auth.authenticate_user("test.radiologist@neuroscan.np", "bad") is None


def test_patient_unique_id_format(tmp_path, monkeypatch):
    db_path = tmp_path / "test_patients.db"
    monkeypatch.setattr(auth, "DB_PATH", db_path)
    auth.init_db()

    patient = auth.create_user(
        "patient.test@neuroscan.np",
        "password123",
        "Test Patient",
        "patient",
    )
    assert patient["patient_unique_id"] == "NSN-PAT-000001"

    found = auth.get_user_by_patient_id("NSN-PAT-000001")
    assert found is not None
    assert found["email"] == "patient.test@neuroscan.np"


def test_create_access_token_roundtrip(tmp_path, monkeypatch):
    db_path = tmp_path / "test_token.db"
    monkeypatch.setattr(auth, "DB_PATH", db_path)
    auth.init_db()

    user = auth.create_user(
        "doctor.test@neuroscan.np",
        "password123",
        "Test Doctor",
        "doctor",
    )
    token = auth.create_access_token(user)
    payload = auth.decode_token(token)
    assert payload["sub"] == user["id"]
    assert payload["role"] == "doctor"
