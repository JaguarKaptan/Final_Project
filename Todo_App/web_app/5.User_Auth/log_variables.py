from enum import Enum

class SecurityAction(Enum):
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted"
    EMAIL_VERIFICATION_SENT = "email_verification_code_sent"
    EMAIL_VERIFIED = "email_verified"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    USER_LOGOUT = "user_logged_out"
    USER_ATTEMPT_DELETE_ACCOUNT = "account_deletion_attemp"
    USER_ATTEMPT_RECOVER_ACCOUNT = "account_recovery_attempt"
    ACCOUNT_RECOVERY_MAIL_SENT = "account_recovery_mail_sent"
    PASSWORD_CHANGED = "password_changed"

class TokenAction(Enum):
    ACCOUNT_DELETION = "account_deletion"
    EMAIL_VERIFICATION = "email_verification"
    ACCOUNT_RECOVERY = "account_recovery"
    PASSWORD_CHANGE = "password_change"

class TokenError(Enum):
    INVALID_TOKEN = "INVALID TOKEN"
    INVALID_TOKEN_TYPE = "INVALID TOKEN TYPE"
    TOKEN_EXPIRED = "TOKEN EXPIRED"

class NoteAction(Enum):
    NOTE_CREATED = "NOTE_CREATED"
    NOTE_TITLE_CHANGED = "NOTE TITLE CHANGED"
    NOTE_CONTENT_CHANGED = "NOTE CONTENT CHANGED"
    NOTE_DELETED = "NOTE DELETED"
    NOTE_TAG_CHANGED = "NOTE TAG CHANGED"
