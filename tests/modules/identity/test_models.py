from decisionos.core.database.base import Base
from decisionos.modules.identity.models import User


def test_user_table_has_expected_columns() -> None:
    columns = User.__table__.columns

    assert User.__tablename__ == "users"
    assert {"id", "created_at", "updated_at"}.issubset(columns.keys())
    assert {
        "email",
        "username",
        "full_name",
        "password_hash",
        "role",
        "auth_provider",
        "is_active",
        "email_verified",
        "last_login_at",
    }.issubset(columns.keys())


def test_user_email_and_username_are_unique_and_indexed() -> None:
    email = User.__table__.c.email
    username = User.__table__.c.username

    assert email.unique is True
    assert email.index is True
    assert username.unique is True
    assert username.index is True


def test_user_model_is_registered_with_application_metadata() -> None:
    assert User.__table__ in Base.metadata.tables.values()
