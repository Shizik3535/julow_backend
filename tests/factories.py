"""
Базовые фабрики для тестирования.

Используется factory_boy для генерации тестовых данных.
Конкретные фабрики создаются в Bounded Context'ах.

Пример:
    user_id = IdFactory()
    email = EmailFactory()
"""

from uuid import uuid4

import factory

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id


class IdFactory(factory.Factory):
    """Фабрика для генерации доменных Id."""

    class Meta:
        model = Id

    value = factory.LazyFunction(uuid4)


class EmailFactory(factory.Factory):
    """Фабрика для генерации доменных Email."""

    class Meta:
        model = Email

    value = factory.Sequence(lambda n: f"user{n}@example.com")


# ── Identity BC Factories ─────────────────────────────────────────────────────

from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class PasswordHashFactory(factory.Factory):
    """Фабрика для генерации PasswordHash."""

    class Meta:
        model = PasswordHash

    value = factory.LazyFunction(lambda: f"$2b$12${uuid4().hex[:53]}")


class VerificationTokenFactory(factory.Factory):
    """Фабрика для генерации VerificationToken."""

    class Meta:
        model = VerificationToken

    value = factory.LazyFunction(lambda: uuid4().hex)


class DeviceInfoFactory(factory.Factory):
    """Фабрика для генерации DeviceInfo."""

    class Meta:
        model = DeviceInfo

    user_agent = factory.Faker("user_agent")
    os = "Windows"
    browser = "Chrome"
    device_type = "desktop"


class RefreshTokenFactory(factory.Factory):
    """Фабрика для генерации RefreshToken."""

    class Meta:
        model = RefreshToken

    value = factory.LazyFunction(lambda: uuid4().hex)


# ── Organization BC Factories ──────────────────────────────────────────────

from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.invitation_token import InvitationToken


class AccentColorFactory(factory.Factory):
    """Фабрика для генерации AccentColor."""

    class Meta:
        model = AccentColor

    hex = factory.LazyFunction(lambda: f"#{uuid4().hex[:6].upper()}")


class InvitationTokenFactory(factory.Factory):
    """Фабрика для генерации InvitationToken."""

    class Meta:
        model = InvitationToken

    value = factory.LazyFunction(lambda: uuid4().hex)
    expires_at = None
    max_uses = None
    used_count = 0


# ── Workspace BC Factories ─────────────────────────────────────────────────

from app.context.workspace.domain.value_objects.invitation_token import InvitationToken as WorkspaceInvitationToken


class WorkspaceInvitationTokenFactory(factory.Factory):
    """Фабрика для генерации InvitationToken (Workspace BC)."""

    class Meta:
        model = WorkspaceInvitationToken

    value = factory.LazyFunction(lambda: uuid4().hex)
    expires_at = None
    max_uses = None
    used_count = 0


# ── Project BC Factories ──────────────────────────────────────────────────

from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.domain.value_objects.category import Category
from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.value_objects.retro_section import RetroSection


class WIPLimitFactory(factory.Factory):
    """Фабрика для генерации WIPLimit."""

    class Meta:
        model = WIPLimit

    value = 5


class SprintGoalFactory(factory.Factory):
    """Фабрика для генерации SprintGoal."""

    class Meta:
        model = SprintGoal

    value = factory.Sequence(lambda n: f"Sprint goal {n}")


class CategoryFactory(factory.Factory):
    """Фабрика для генерации Category."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class CustomFieldDefinitionFactory(factory.Factory):
    """Фабрика для генерации CustomFieldDefinition."""

    class Meta:
        model = CustomFieldDefinition

    name = factory.Sequence(lambda n: f"field_{n}")


class RetroSectionFactory(factory.Factory):
    """Фабрика для генерации RetroSection."""

    class Meta:
        model = RetroSection

    title = factory.Sequence(lambda n: f"Section {n}")


# ── Task BC Factories ──────────────────────────────────────────────────────

from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.task_progress import TaskProgress
from app.context.task.domain.value_objects.effort_estimate import EffortEstimate
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_unit import EffortUnit
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


class LabelFactory(factory.Factory):
    """Фабрика для генерации Label."""

    class Meta:
        model = Label

    name = factory.Sequence(lambda n: f"label_{n}")
    color = None


class TaskProgressFactory(factory.Factory):
    """Фабрика для генерации TaskProgress."""

    class Meta:
        model = TaskProgress

    value = 50


class EffortEstimateFactory(factory.Factory):
    """Фабрика для генерации EffortEstimate."""

    class Meta:
        model = EffortEstimate

    value = 8.0
    unit = EffortUnit.HOURS


class ActualEffortFactory(factory.Factory):
    """Фабрика для генерации ActualEffort."""

    class Meta:
        model = ActualEffort

    value = 5.0
    unit = EffortUnit.HOURS


class RecurrenceConfigFactory(factory.Factory):
    """Фабрика для генерации RecurrenceConfig."""

    class Meta:
        model = RecurrenceConfig

    pattern = RecurrencePattern.WEEKLY
    interval = 1
    end_date = None
    max_occurrences = None


# ── ORM Factories ────────────────────────────────────────────────────────────
# ORM-фабрики используются в integration-тестах.
# Они создают объекты ORM-моделей для записи в БД.
#
# Пример:
#
# class UserORMFactory(factory.alchemy.SQLAlchemyModelFactory):
#     class Meta:
#         model = UserORMModel
#         sqlalchemy_session = None  # устанавливается в conftest
#         sqlalchemy_session_persistence = "commit"
#
#     id = factory.LazyFunction(uuid4)
#     email = factory.Sequence(lambda n: f"user{n}@example.com")
