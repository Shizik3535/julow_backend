from app.context.identity.presentation.schemas.requests.add_trusted_device_request import (
    AddTrustedDeviceRequest,
)
from app.context.identity.presentation.schemas.requests.change_password_request import (
    ChangePasswordRequest,
)
from app.context.identity.presentation.schemas.requests.confirm_email_request import (
    ConfirmEmailRequest,
)
from app.context.identity.presentation.schemas.requests.disable_auth_factor_request import (
    DisableAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.enable_auth_factor_request import (
    EnableAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.generate_backup_codes_request import (
    GenerateBackupCodesRequest,
)
from app.context.identity.presentation.schemas.requests.link_oauth_request import LinkOAuthRequest
from app.context.identity.presentation.schemas.requests.login_request import LoginRequest
from app.context.identity.presentation.schemas.requests.password_reset_confirm_request import (
    PasswordResetConfirmRequest,
)
from app.context.identity.presentation.schemas.requests.password_reset_request import (
    RequestPasswordResetRequest,
)
from app.context.identity.presentation.schemas.requests.refresh_session_request import (
    RefreshSessionRequest,
)
from app.context.identity.presentation.schemas.requests.register_request import RegisterRequest
from app.context.identity.presentation.schemas.requests.set_primary_auth_factor_request import (
    SetPrimaryAuthFactorRequest,
)
from app.context.identity.presentation.schemas.requests.terminate_all_sessions_request import (
    TerminateAllSessionsRequest,
)
from app.context.identity.presentation.schemas.requests.use_backup_code_request import (
    UseBackupCodeRequest,
)
from app.context.identity.presentation.schemas.requests.verify_auth_factor_request import (
    VerifyAuthFactorRequest,
)

__all__ = [
    "AddTrustedDeviceRequest",
    "ChangePasswordRequest",
    "ConfirmEmailRequest",
    "DisableAuthFactorRequest",
    "EnableAuthFactorRequest",
    "GenerateBackupCodesRequest",
    "LinkOAuthRequest",
    "LoginRequest",
    "PasswordResetConfirmRequest",
    "RefreshSessionRequest",
    "RegisterRequest",
    "RequestPasswordResetRequest",
    "SetPrimaryAuthFactorRequest",
    "TerminateAllSessionsRequest",
    "UseBackupCodeRequest",
    "VerifyAuthFactorRequest",
]
