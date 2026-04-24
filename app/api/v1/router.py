from fastapi import APIRouter

# Единое место для сборки всех endpoint'ов API v1.
#
# Каждый Bounded Context регистрирует свои роуты через
# включение своего APIRouter в этот корневой роутер.
#
# Порядок включения определяет порядок в OpenAPI документации.
#
# При переходе на микросервисы — каждый BC получает свой
# собственный router.py, а этот файл удаляется.


api_v1_router = APIRouter()

# --- Регистрация роутов Bounded Context'ов ---

# Identity BC
from app.context.identity.presentation.controllers import (
    AccountController,
    AdminController,
    AuthController,
    SecurityController,
)

_auth_controller = AuthController()
_account_controller = AccountController()
_security_controller = SecurityController()
_admin_controller = AdminController()

api_v1_router.include_router(_auth_controller.router)
api_v1_router.include_router(_account_controller.router)
api_v1_router.include_router(_security_controller.router)
api_v1_router.include_router(_admin_controller.router)

# Profile BC
from app.context.profile.presentation.controllers import ProfileController

_profile_controller = ProfileController()

api_v1_router.include_router(_profile_controller.router)
