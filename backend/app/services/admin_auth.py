import os


def is_admin_email(email: str) -> bool:
    if not email:
        return False
    allowlist = [item.strip().lower() for item in os.getenv("ADMIN_EMAILS", "").split(",") if item.strip()]
    return email.strip().lower() in allowlist
