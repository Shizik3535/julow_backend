from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Path, UploadFile

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.profile.application.commands.add_social_link import (
    AddSocialLinkCommand,
    AddSocialLinkHandler,
)
from app.context.profile.application.commands.change_avatar import (
    ChangeAvatarCommand,
    ChangeAvatarHandler,
)
from app.context.profile.application.commands.pin_item import PinItemCommand, PinItemHandler
from app.context.profile.application.commands.reorder_pinned_items import (
    ReorderPinnedItemsCommand,
    ReorderPinnedItemsHandler,
)
from app.context.profile.application.commands.remove_social_link import (
    RemoveSocialLinkCommand,
    RemoveSocialLinkHandler,
)
from app.context.profile.application.commands.unpin_item import UnpinItemCommand, UnpinItemHandler
from app.context.profile.application.commands.update_appearance import (
    UpdateAppearanceCommand,
    UpdateAppearanceHandler,
)
from app.context.profile.application.commands.update_hotkeys import (
    HotkeyInput as HotkeyCommandInput,
    UpdateHotkeysCommand,
    UpdateHotkeysHandler,
)
from app.context.profile.application.commands.update_localization import (
    UpdateLocalizationCommand,
    UpdateLocalizationHandler,
)
from app.context.profile.application.commands.update_navigation import (
    UpdateNavigationCommand,
    UpdateNavigationHandler,
)
from app.context.profile.application.commands.update_personal_info import (
    UpdatePersonalInfoCommand,
    UpdatePersonalInfoHandler,
)
from app.context.profile.application.commands.update_privacy import (
    UpdatePrivacyCommand,
    UpdatePrivacyHandler,
)
from app.context.profile.application.commands.update_sidebar import (
    SidebarSectionInput as SidebarSectionCommandInput,
    UpdateSidebarCommand,
    UpdateSidebarHandler,
)
from app.context.profile.application.queries.get_profile import (
    GetProfileHandler,
    GetProfileQuery,
)
from app.context.profile.application.queries.get_public_profile import (
    GetPublicProfileHandler,
    GetPublicProfileQuery,
)
from app.context.profile.application.queries.search_profiles import (
    SearchProfilesHandler,
    SearchProfilesQuery,
)
from app.context.profile.presentation.dependencies import (
    get_current_user_id,
    get_file_storage_port,
    get_organization_membership_port,
    get_profile_event_bus,
    get_profile_repository,
    get_start_page_registry_port,
)
from app.context.profile.presentation.schemas.requests.add_social_link_request import (
    AddSocialLinkRequest,
)
from app.context.profile.presentation.schemas.requests.pin_item_request import PinItemRequest
from app.context.profile.presentation.schemas.requests.reorder_pinned_items_request import (
    ReorderPinnedItemsRequest,
)
from app.context.profile.presentation.schemas.requests.update_appearance_request import (
    UpdateAppearanceRequest,
)
from app.context.profile.presentation.schemas.requests.update_hotkeys_request import (
    UpdateHotkeysRequest,
)
from app.context.profile.presentation.schemas.requests.update_localization_request import (
    UpdateLocalizationRequest,
)
from app.context.profile.presentation.schemas.requests.update_navigation_request import (
    UpdateNavigationRequest,
)
from app.context.profile.presentation.schemas.requests.update_personal_info_request import (
    UpdatePersonalInfoRequest,
)
from app.context.profile.presentation.schemas.requests.update_privacy_request import (
    UpdatePrivacyRequest,
)
from app.context.profile.presentation.schemas.requests.update_sidebar_request import (
    UpdateSidebarRequest,
)
from app.context.profile.presentation.schemas.responses.profile_response import ProfileResponse
from app.context.profile.presentation.schemas.responses.public_profile_response import PublicProfileResponse
from app.context.profile.presentation.schemas.responses.profile_settings_response import (
    AppearanceSettingsResponse,
    HotkeyResponse,
    LocalizationSettingsResponse,
    NavigationSettingsResponse,
    PinnedItemResponse,
    PrivacySettingsResponse,
    ProfileSettingsResponse,
    SidebarSectionResponse,
)


class ProfileController(BaseController):
    """
    Контроллер профиля пользователя (Profile BC).

    Endpoint'ы:
        GET    /profile/me                           — Получить свой профиль
        GET    /profile/me/settings                   — Получить настройки профиля
        GET    /profile/{user_id}                     — Получить публичный профиль пользователя
        GET    /profile/search                        — Поиск профилей (admin)
        PATCH  /profile/me/personal-info              — Обновить персональные данные
        POST   /profile/me/avatar                     — Изменить аватар
        POST   /profile/me/social-links               — Добавить социальную ссылку
        DELETE /profile/me/social-links/{platform}    — Удалить социальную ссылку
        PUT    /profile/me/appearance                 — Обновить настройки внешнего вида
        PUT    /profile/me/localization               — Обновить настройки локализации
        PUT    /profile/me/navigation                 — Обновить настройки навигации
        PUT    /profile/me/privacy                    — Обновить настройки приватности
        PUT    /profile/me/hotkeys                    — Обновить горячие клавиши
        PUT    /profile/me/sidebar                    — Обновить конфигурацию sidebar
        POST   /profile/me/pinned                     — Закрепить элемент
        DELETE /profile/me/pinned/{target_type}/{target_id} — Открепить элемент
        PUT    /profile/me/pinned/reorder               — Переупорядочить закреплённые
    """

    def __init__(self) -> None:
        super().__init__(prefix="/profile", tags=["Profile"])

    def _register_routes(self) -> None:
        # --- Profile ---
        self._router.add_api_route(
            "/me",
            self.get_my_profile,
            methods=["GET"],
            response_model=SuccessResponse[ProfileResponse],
            summary="Получить свой профиль",
            description=(
                "Возвращает данные профиля аутентифицированного пользователя. "
                "Включает аватар, bio, должность и временные метки."
            ),
            responses={
                200: {"description": "Данные профиля"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/settings",
            self.get_my_settings,
            methods=["GET"],
            response_model=SuccessResponse[ProfileSettingsResponse],
            summary="Получить настройки профиля",
            description=(
                "Возвращает все настройки профиля: внешний вид, локализацию, "
                "навигацию, приватность, горячие клавиши, sidebar, закреплённые."
            ),
            responses={
                200: {"description": "Настройки профиля"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/search",
            self.search_profiles,
            methods=["GET"],
            response_model=PaginatedResponse[ProfileResponse],
            summary="Поиск профилей",
            description="Пагинированный поиск профилей с фильтрацией.",
            responses={
                200: {"description": "Список профилей"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )

        # --- Personal info ---
        self._router.add_api_route(
            "/me/personal-info",
            self.update_personal_info,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить персональные данные",
            description=(
                "Обновляет персональные данные профиля: bio и/или job_title. "
                "Передаются только поля, которые нужно изменить. "
                "Значения `null` не изменяют поле."
            ),
            responses={
                200: {"description": "Данные обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Avatar ---
        self._router.add_api_route(
            "/me/avatar",
            self.change_avatar,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Изменить аватар",
            description="Загружает новый аватар пользователя в файловое хранилище.",
            responses={
                200: {"description": "Аватар обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Social links ---
        self._router.add_api_route(
            "/me/social-links",
            self.add_social_link,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить социальную ссылку",
            description="Добавляет ссылку на профиль в социальной сети.",
            responses={
                200: {"description": "Ссылка добавлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                409: {"description": "Ссылка уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/social-links/{platform}",
            self.remove_social_link,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить социальную ссылку",
            description="Удаляет ссылку на профиль в указанной социальной сети.",
            responses={
                200: {"description": "Ссылка удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден / ссылка не найдена", "model": ErrorResponse},
            },
        )

        # --- Appearance ---
        self._router.add_api_route(
            "/me/appearance",
            self.update_appearance,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки внешнего вида",
            description=(
                "Заменяет группу настроек внешнего вида целиком: "
                "тема оформления, акцентный цвет, плотность интерфейса."
            ),
            responses={
                200: {"description": "Настройки обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Localization ---
        self._router.add_api_route(
            "/me/localization",
            self.update_localization,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки локализации",
            description=(
                "Заменяет группу настроек локализации целиком: "
                "язык, часовой пояс, формат даты, формат времени, день начала недели."
            ),
            responses={
                200: {"description": "Настройки обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Navigation ---
        self._router.add_api_route(
            "/me/navigation",
            self.update_navigation,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки навигации",
            description="Заменяет настройки навигации: идентификатор стартовой страницы.",
            responses={
                200: {"description": "Настройки обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации / страница не зарегистрирована", "model": ErrorResponse},
            },
        )

        # --- Privacy ---
        self._router.add_api_route(
            "/me/privacy",
            self.update_privacy,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить настройки приватности",
            description=(
                "Заменяет группу настроек приватности целиком: "
                "видимость профиля, видимость онлайн-статуса, "
                "согласие на отслеживание активности."
            ),
            responses={
                200: {"description": "Настройки обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Hotkeys ---
        self._router.add_api_route(
            "/me/hotkeys",
            self.update_hotkeys,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить горячие клавиши",
            description="Заменяет конфигурацию горячих клавиш целиком.",
            responses={
                200: {"description": "Горячие клавиши обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Sidebar ---
        self._router.add_api_route(
            "/me/sidebar",
            self.update_sidebar,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Обновить конфигурацию sidebar",
            description="Заменяет конфигурацию секций sidebar целиком.",
            responses={
                200: {"description": "Sidebar обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Pinned items ---
        self._router.add_api_route(
            "/me/pinned",
            self.pin_item,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Закрепить элемент",
            description="Закрепляет элемент (workspace, project, task и т.д.) в профиле.",
            responses={
                200: {"description": "Элемент закреплён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                409: {"description": "Элемент уже закреплён", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/pinned/{target_type}/{target_id}",
            self.unpin_item,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Открепить элемент",
            description="Открепляет ранее закреплённый элемент.",
            responses={
                200: {"description": "Элемент откреплён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/pinned/reorder",
            self.reorder_pinned_items,
            methods=["PUT"],
            response_model=MessageResponse,
            summary="Переупорядочить закреплённые элементы",
            description="Изменяет порядок закреплённых элементов. Передаётся список target_id в желаемом порядке.",
            responses={
                200: {"description": "Порядок обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

        # --- Public profile (last to avoid shadowing specific routes) ---
        self._router.add_api_route(
            "/{user_id}",
            self.get_public_profile,
            methods=["GET"],
            response_model=SuccessResponse[PublicProfileResponse],
            summary="Получить публичный профиль пользователя",
            description=(
                "Возвращает публичные данные профиля другого пользователя. "
                "Видимость определяется настройкой privacy.profile_visibility владельца: "
                "PUBLIC — всем; ORGANIZATION_ONLY — членам общей организации; "
                "PRIVATE — только владельцу. При отсутствии прав возвращается 404 "
                "(существование скрытого профиля не раскрывается)."
            ),
            responses={
                200: {"description": "Публичные данные профиля"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Профиль не найден или недоступен", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    async def get_my_profile(
        self,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
    ) -> SuccessResponse[ProfileResponse]:
        """Получить профиль текущего пользователя."""
        handler = GetProfileHandler(profile_repo=profile_repo)
        query = GetProfileQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ProfileResponse.model_validate(dto.model_dump()))

    async def get_my_settings(
        self,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
    ) -> SuccessResponse[ProfileSettingsResponse]:
        """Получить настройки профиля текущего пользователя."""
        handler = GetProfileHandler(profile_repo=profile_repo)
        query = GetProfileQuery(user_id=user_id)
        dto = await handler.handle(query)
        settings = ProfileSettingsResponse(
            user_id=dto.user_id,
            appearance=AppearanceSettingsResponse(**dto.appearance),
            localization=LocalizationSettingsResponse(**dto.localization),
            navigation=NavigationSettingsResponse(**dto.navigation),
            privacy=PrivacySettingsResponse(**dto.privacy),
            hotkeys=[
                HotkeyResponse(action=hk["action"], key_combination=hk["key_combination"], is_enabled=hk["is_enabled"])
                for hk in dto.hotkeys
            ],
            sidebar_sections=[
                SidebarSectionResponse(
                    section_id=ss["section_id"],
                    is_collapsed=ss["is_collapsed"],
                    item_ids=ss["item_ids"],
                    order=ss["order"],
                )
                for ss in dto.sidebar_sections
            ],
            pinned_items=[
                PinnedItemResponse(
                    target_type=pi["target_type"],
                    target_id=pi["target_id"],
                    order=pi["order"],
                    pinned_at=pi["pinned_at"],
                )
                for pi in dto.pinned_items
            ],
        )
        return SuccessResponse(data=settings)

    async def get_public_profile(
        self,
        user_id: UUID = Path(..., description="UUID пользователя"),
        requester_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        org_membership_port=Depends(get_organization_membership_port),
    ) -> SuccessResponse[PublicProfileResponse]:
        """Получить публичный профиль другого пользователя."""
        handler = GetPublicProfileHandler(
            profile_repo=profile_repo,
            org_membership_port=org_membership_port,
        )
        query = GetPublicProfileQuery(user_id=str(user_id), requester_id=requester_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=PublicProfileResponse.model_validate(dto.model_dump()))

    async def search_profiles(
        self,
        offset: int = 0,
        limit: int = 100,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
    ) -> PaginatedResponse[ProfileResponse]:
        """Поиск профилей с пагинацией."""
        handler = SearchProfilesHandler(profile_repo=profile_repo)
        query = SearchProfilesQuery(offset=offset, limit=limit)
        dto = await handler.handle(query)
        items = [ProfileResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(
            items=items,
            total=dto.total,
            page=page,
            page_size=limit,
        )

    # ------------------------------------------------------------------
    # Personal info
    # ------------------------------------------------------------------

    async def update_personal_info(
        self,
        body: UpdatePersonalInfoRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить персональные данные профиля."""
        handler = UpdatePersonalInfoHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = UpdatePersonalInfoCommand(
            user_id=user_id,
            display_name=body.display_name,
            bio=body.bio,
            job_title=body.job_title,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Персональные данные обновлены"})

    # ------------------------------------------------------------------
    # Avatar
    # ------------------------------------------------------------------

    async def change_avatar(
        self,
        file: UploadFile,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        file_storage=Depends(get_file_storage_port),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Изменить аватар пользователя."""
        file_data = await file.read()
        handler = ChangeAvatarHandler(
            profile_repo=profile_repo,
            file_storage=file_storage,
            event_bus=event_bus,
        )
        command = ChangeAvatarCommand(
            user_id=user_id,
            file_data=file_data,
            content_type=file.content_type or "image/png",
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Аватар обновлён"})

    # ------------------------------------------------------------------
    # Social links
    # ------------------------------------------------------------------

    async def add_social_link(
        self,
        body: AddSocialLinkRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Добавить социальную ссылку."""
        handler = AddSocialLinkHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = AddSocialLinkCommand(
            user_id=user_id,
            platform=body.platform,
            url=body.url,
            display_name=body.display_name,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Социальная ссылка добавлена"})

    async def remove_social_link(
        self,
        platform: str,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Удалить социальную ссылку."""
        handler = RemoveSocialLinkHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = RemoveSocialLinkCommand(
            user_id=user_id,
            platform=platform,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Социальная ссылка удалена"})

    # ------------------------------------------------------------------
    # Appearance
    # ------------------------------------------------------------------

    async def update_appearance(
        self,
        body: UpdateAppearanceRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить настройки внешнего вида."""
        handler = UpdateAppearanceHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = UpdateAppearanceCommand(
            user_id=user_id,
            theme=body.theme,
            accent_color=body.accent_color,
            interface_density=body.interface_density,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Настройки внешнего вида обновлены"})

    # ------------------------------------------------------------------
    # Localization
    # ------------------------------------------------------------------

    async def update_localization(
        self,
        body: UpdateLocalizationRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить настройки локализации."""
        handler = UpdateLocalizationHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = UpdateLocalizationCommand(
            user_id=user_id,
            language=body.language,
            timezone=body.timezone,
            date_format=body.date_format,
            time_format=body.time_format,
            week_start_day=body.week_start_day,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Настройки локализации обновлены"})

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def update_navigation(
        self,
        body: UpdateNavigationRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        start_page_registry=Depends(get_start_page_registry_port),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить настройки навигации."""
        handler = UpdateNavigationHandler(
            profile_repo=profile_repo,
            start_page_registry=start_page_registry,
            event_bus=event_bus,
        )
        command = UpdateNavigationCommand(
            user_id=user_id,
            start_page=body.start_page,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Настройки навигации обновлены"})

    # ------------------------------------------------------------------
    # Privacy
    # ------------------------------------------------------------------

    async def update_privacy(
        self,
        body: UpdatePrivacyRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить настройки приватности."""
        handler = UpdatePrivacyHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = UpdatePrivacyCommand(
            user_id=user_id,
            profile_visibility=body.profile_visibility,
            online_status_visibility=body.online_status_visibility,
            activity_tracking_consent=body.activity_tracking_consent,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Настройки приватности обновлены"})

    # ------------------------------------------------------------------
    # Hotkeys
    # ------------------------------------------------------------------

    async def update_hotkeys(
        self,
        body: UpdateHotkeysRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить горячие клавиши."""
        handler = UpdateHotkeysHandler(profile_repo=profile_repo, event_bus=event_bus)
        hotkeys = [
            HotkeyCommandInput(
                action=h.action,
                key_combination=h.key_combination,
                is_enabled=h.is_enabled,
            )
            for h in body.hotkeys
        ]
        command = UpdateHotkeysCommand(user_id=user_id, hotkeys=hotkeys)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Горячие клавиши обновлены"})

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------

    async def update_sidebar(
        self,
        body: UpdateSidebarRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Обновить конфигурацию sidebar."""
        handler = UpdateSidebarHandler(profile_repo=profile_repo, event_bus=event_bus)
        sections = [
            SidebarSectionCommandInput(
                section_id=s.section_id,
                is_collapsed=s.is_collapsed,
                item_ids=s.item_ids,
                order=s.order,
            )
            for s in body.sections
        ]
        command = UpdateSidebarCommand(user_id=user_id, sections=sections)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Sidebar обновлён"})

    # ------------------------------------------------------------------
    # Pinned items
    # ------------------------------------------------------------------

    async def pin_item(
        self,
        body: PinItemRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Закрепить элемент."""
        handler = PinItemHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = PinItemCommand(
            user_id=user_id,
            target_type=body.target_type,
            target_id=body.target_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Элемент закреплён"})

    async def unpin_item(
        self,
        target_type: str,
        target_id: str,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Открепить элемент."""
        handler = UnpinItemHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = UnpinItemCommand(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Элемент откреплён"})

    async def reorder_pinned_items(
        self,
        body: ReorderPinnedItemsRequest,
        user_id: str = Depends(get_current_user_id),
        profile_repo=Depends(get_profile_repository),
        event_bus=Depends(get_profile_event_bus),
    ) -> MessageResponse:
        """Переупорядочить закреплённые элементы."""
        handler = ReorderPinnedItemsHandler(profile_repo=profile_repo, event_bus=event_bus)
        command = ReorderPinnedItemsCommand(
            user_id=user_id,
            ordered_ids=body.ordered_ids,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Порядок закреплённых элементов обновлён"})
