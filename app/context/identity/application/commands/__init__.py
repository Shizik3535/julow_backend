from app.context.identity.application.commands.add_trusted_device import (
    AddTrustedDeviceCommand,
    AddTrustedDeviceHandler,
)
from app.context.identity.application.commands.assign_role import (
    AssignRoleCommand,
    AssignRoleHandler,
)
from app.context.identity.application.commands.cancel_account_deletion import (
    CancelAccountDeletionCommand,
    CancelAccountDeletionHandler,
)
from app.context.identity.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordHandler,
)
from app.context.identity.application.commands.confirm_email import (
    ConfirmEmailCommand,
    ConfirmEmailHandler,
)
from app.context.identity.application.commands.create_session import (
    CreateSessionCommand,
    CreateSessionHandler,
)
from app.context.identity.application.commands.disable_account import (
    DisableAccountCommand,
    DisableAccountHandler,
)
from app.context.identity.application.commands.disable_auth_factor import (
    DisableAuthFactorCommand,
    DisableAuthFactorHandler,
)
from app.context.identity.application.commands.enable_auth_factor import (
    EnableAuthFactorCommand,
    EnableAuthFactorHandler,
)
from app.context.identity.application.commands.generate_backup_codes import (
    GenerateBackupCodesCommand,
    GenerateBackupCodesHandler,
)
from app.context.identity.application.commands.link_oauth import (
    LinkOAuthCommand,
    LinkOAuthHandler,
)
from app.context.identity.application.commands.login_user import (
    LoginUserCommand,
    LoginUserHandler,
)
from app.context.identity.application.commands.reactivate_account import (
    ReactivateAccountCommand,
    ReactivateAccountHandler,
)
from app.context.identity.application.commands.refresh_session import (
    RefreshSessionCommand,
    RefreshSessionHandler,
)
from app.context.identity.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from app.context.identity.application.commands.remove_role import (
    RemoveRoleCommand,
    RemoveRoleHandler,
)
from app.context.identity.application.commands.remove_trusted_device import (
    RemoveTrustedDeviceCommand,
    RemoveTrustedDeviceHandler,
)
from app.context.identity.application.commands.request_account_deletion import (
    RequestAccountDeletionCommand,
    RequestAccountDeletionHandler,
)
from app.context.identity.application.commands.request_password_reset import (
    RequestPasswordResetCommand,
    RequestPasswordResetHandler,
)
from app.context.identity.application.commands.reset_password import (
    ResetPasswordCommand,
    ResetPasswordHandler,
)
from app.context.identity.application.commands.set_primary_auth_factor import (
    SetPrimaryAuthFactorCommand,
    SetPrimaryAuthFactorHandler,
)
from app.context.identity.application.commands.terminate_all_sessions import (
    TerminateAllSessionsCommand,
    TerminateAllSessionsHandler,
)
from app.context.identity.application.commands.terminate_session import (
    TerminateSessionCommand,
    TerminateSessionHandler,
)
from app.context.identity.application.commands.unlink_oauth import (
    UnlinkOAuthCommand,
    UnlinkOAuthHandler,
)
from app.context.identity.application.commands.unlock_account import (
    UnlockAccountCommand,
    UnlockAccountHandler,
)
from app.context.identity.application.commands.use_backup_code import (
    UseBackupCodeCommand,
    UseBackupCodeHandler,
)
from app.context.identity.application.commands.verify_auth_factor import (
    VerifyAuthFactorCommand,
    VerifyAuthFactorHandler,
)

__all__ = [
    "AddTrustedDeviceCommand",
    "AddTrustedDeviceHandler",
    "AssignRoleCommand",
    "AssignRoleHandler",
    "CancelAccountDeletionCommand",
    "CancelAccountDeletionHandler",
    "ChangePasswordCommand",
    "ChangePasswordHandler",
    "ConfirmEmailCommand",
    "ConfirmEmailHandler",
    "CreateSessionCommand",
    "CreateSessionHandler",
    "DisableAccountCommand",
    "DisableAccountHandler",
    "DisableAuthFactorCommand",
    "DisableAuthFactorHandler",
    "EnableAuthFactorCommand",
    "EnableAuthFactorHandler",
    "GenerateBackupCodesCommand",
    "GenerateBackupCodesHandler",
    "LinkOAuthCommand",
    "LinkOAuthHandler",
    "LoginUserCommand",
    "LoginUserHandler",
    "ReactivateAccountCommand",
    "ReactivateAccountHandler",
    "RefreshSessionCommand",
    "RefreshSessionHandler",
    "RegisterUserCommand",
    "RegisterUserHandler",
    "RemoveRoleCommand",
    "RemoveRoleHandler",
    "RemoveTrustedDeviceCommand",
    "RemoveTrustedDeviceHandler",
    "RequestAccountDeletionCommand",
    "RequestAccountDeletionHandler",
    "RequestPasswordResetCommand",
    "RequestPasswordResetHandler",
    "ResetPasswordCommand",
    "ResetPasswordHandler",
    "SetPrimaryAuthFactorCommand",
    "SetPrimaryAuthFactorHandler",
    "TerminateAllSessionsCommand",
    "TerminateAllSessionsHandler",
    "TerminateSessionCommand",
    "TerminateSessionHandler",
    "UnlinkOAuthCommand",
    "UnlinkOAuthHandler",
    "UnlockAccountCommand",
    "UnlockAccountHandler",
    "UseBackupCodeCommand",
    "UseBackupCodeHandler",
    "VerifyAuthFactorCommand",
    "VerifyAuthFactorHandler",
]
