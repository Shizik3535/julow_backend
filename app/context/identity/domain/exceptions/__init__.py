from app.context.identity.domain.exceptions.user_exceptions import (
    AccountDeletionPendingException,
    CannotUnlinkLastProviderException,
    DuplicateRoleException,
    EmailNotConfirmedException,
    InvalidBackupCodeException,
    InvalidCredentialsException,
    InvalidVerificationTokenException,
    LastSystemRoleException,
    RoleNotFoundException,
    UserBlockedException,
    UserNotFoundException,
)
from app.context.identity.domain.exceptions.auth_exceptions import (
    InvalidTwoFACodeException,
    OAuthProviderAlreadyLinkedException,
    TwoFARequiredException,
)
from app.context.identity.domain.exceptions.session_exceptions import (
    InactiveSessionException,
    SessionExpiredException,
    SessionNotFoundException,
    UnauthorizedSessionAccessException,
)

__all__ = [
    "AccountDeletionPendingException",
    "CannotUnlinkLastProviderException",
    "DuplicateRoleException",
    "EmailNotConfirmedException",
    "InactiveSessionException",
    "InvalidBackupCodeException",
    "InvalidCredentialsException",
    "InvalidTwoFACodeException",
    "InvalidVerificationTokenException",
    "LastSystemRoleException",
    "OAuthProviderAlreadyLinkedException",
    "RoleNotFoundException",
    "SessionExpiredException",
    "SessionNotFoundException",
    "TwoFARequiredException",
    "UnauthorizedSessionAccessException",
    "UserBlockedException",
    "UserNotFoundException",
]
