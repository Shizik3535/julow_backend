from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di.container import Container
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.application.ports.auth.auth_port import AuthTokenPort

_bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT access-токен в формате `Bearer <token>`",
    auto_error=False,
)


def get_container(request: Request) -> Container:
    """Извлечь DI-контейнер из FastAPI application state."""
    return request.app.state.container


# ---------------------------------------------------------------------------
# Database session (per-request)
# ---------------------------------------------------------------------------


async def get_db_session(
    container: Container = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    """Per-request AsyncSession с автоматическим commit/rollback."""
    session_factory = container.db_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Analytics BC — Repositories
# ---------------------------------------------------------------------------


async def get_dashboard_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.dashboard_repo(session=session)


async def get_dashboard_template_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.dashboard_template_repo(session=session)


async def get_report_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.report_repo(session=session)


async def get_report_job_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.report_job_repo(session=session)


# ---------------------------------------------------------------------------
# Analytics BC — per-request provider chains (FastAPI deps so each is
# resolved once per request and shared between consumers).
# ---------------------------------------------------------------------------


async def get_workspace_membership_provider(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Workspace membership provider bound to the per-request session."""
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    return container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )


async def get_workspace_provider(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Workspace provider bound to the per-request session."""
    ws_repo = container.workspace_repo(session=session)
    return container.workspace_provider(repo=ws_repo)


async def get_sprint_provider(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Sprint provider bound to the per-request session."""
    sprint_repo = container.sprint_repo(session=session)
    return container.sprint_provider(repo=sprint_repo)


async def get_project_provider(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Project provider bound to the per-request session."""
    project_repo = container.project_repo(session=session)
    return container.project_provider(repo=project_repo)


async def get_file_attachment_provider(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """FileStorage attachment provider bound to the per-request session."""
    file_repo = container.file_repo(session=session)
    storage_repo = container.storage_repo(session=session)
    return container.file_attachment_provider(
        file_repo=file_repo,
        storage_repo=storage_repo,
    )


# ---------------------------------------------------------------------------
# Analytics BC — Authorization
# ---------------------------------------------------------------------------


async def get_analytics_permission_checker(
    container: Container = Depends(get_container),
    membership_provider=Depends(get_workspace_membership_provider),
):
    return container.analytics_permission_checker_port(
        workspace_membership_provider=membership_provider,
    )


# ---------------------------------------------------------------------------
# Analytics BC — Integration ports (inboard)
# ---------------------------------------------------------------------------


async def get_analytics_workspace_port(
    container: Container = Depends(get_container),
    workspace_provider=Depends(get_workspace_provider),
    membership_provider=Depends(get_workspace_membership_provider),
):
    return container.analytics_workspace_port(
        workspace_provider=workspace_provider,
        workspace_membership_provider=membership_provider,
    )


async def get_analytics_project_port(
    container: Container = Depends(get_container),
    project_provider=Depends(get_project_provider),
):
    return container.analytics_project_port(
        project_provider=project_provider,
    )


async def get_analytics_task_analytics_port(
    container: Container = Depends(get_container),
):
    return container.analytics_task_analytics_port()


async def get_analytics_timetracking_analytics_port(
    container: Container = Depends(get_container),
):
    return container.analytics_timetracking_analytics_port()


async def get_analytics_sprint_port(
    container: Container = Depends(get_container),
    sprint_provider=Depends(get_sprint_provider),
):
    return container.analytics_sprint_port(
        sprint_provider=sprint_provider,
    )


async def get_analytics_file_attachment_port(
    container: Container = Depends(get_container),
    file_attachment_provider=Depends(get_file_attachment_provider),
):
    return container.analytics_file_attachment_port(
        file_attachment_provider=file_attachment_provider,
    )


# ---------------------------------------------------------------------------
# Analytics BC — Query execution
# ---------------------------------------------------------------------------


async def get_analytics_query_executor_port(
    container: Container = Depends(get_container),
    analytics_sprint_port=Depends(get_analytics_sprint_port),
):
    # All data-path analytics ports (workspace/project/task/timetracking)
    # use ``session_factory`` internally and don't need a per-request
    # session override. Only ``analytics_sprint_port`` depends on a repo,
    # so we override it here and rebuild ``task_analytics_resolver`` —
    # other resolvers come straight from the container default.
    #
    # NOTE: when adding a new resolver, register it in ``container.py``
    # (``analytics_query_executor_port.resolvers``) AND keep the override
    # set below in sync if it requires a session-bound port.
    task_analytics_resolver = container.task_analytics_resolver(
        sprint_port=analytics_sprint_port,
    )
    return container.analytics_query_executor_port(
        resolvers=[
            container.workspace_analytics_resolver(),
            container.project_analytics_resolver(),
            task_analytics_resolver,
            container.timetracking_analytics_resolver(),
        ],
    )


# ---------------------------------------------------------------------------
# Analytics BC — Report generation
# ---------------------------------------------------------------------------


async def get_report_generator_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.report_generator_port(
        report_repo=container.report_repo(session=session),
        job_repo=container.report_job_repo(session=session),
    )


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    return container.auth_token_port()


async def get_analytics_event_bus(container: Container = Depends(get_container)):
    return container.analytics_event_bus()


async def get_analytics_schema_port(container: Container = Depends(get_container)):
    """Получить AnalyticsSchemaPort (Singleton, без состояния)."""
    return container.analytics_schema_port()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_token_port: AuthTokenPort = Depends(get_auth_token_port),
) -> str:
    """Извлечь user_id из JWT access-токена."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Не аутентифицирован — отсутствует Authorization заголовок",
        )
    try:
        payload = auth_token_port.validate_access_token(credentials.credentials)
    except InvalidTokenException:
        raise HTTPException(
            status_code=401,
            detail="Невалидный или просроченный access-токен",
        )
    return str(payload.user_id)
