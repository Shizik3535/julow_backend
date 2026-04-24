"""Unit-тесты для LocalizationSettings."""

import pytest

from app.shared.domain.value_objects.language_code_vo import LanguageCode
from app.shared.domain.value_objects.timezone_vo import Timezone
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.date_format import DateFormat
from app.context.profile.domain.value_objects.time_format import TimeFormat
from app.context.profile.domain.value_objects.week_start_day import WeekStartDay


@pytest.mark.unit
class TestLocalizationSettings:
    def test_defaults(self) -> None:
        settings = LocalizationSettings()
        assert settings.language == LanguageCode("en")
        assert settings.timezone == Timezone("UTC")
        assert settings.date_format == DateFormat("YYYY-MM-DD")
        assert settings.time_format == TimeFormat.H24
        assert settings.week_start_day == WeekStartDay.MONDAY

    def test_custom_settings(self) -> None:
        settings = LocalizationSettings(
            language=LanguageCode("ru"),
            timezone=Timezone("Europe/Moscow"),
            date_format=DateFormat("DD.MM.YYYY"),
            time_format=TimeFormat.H12,
            week_start_day=WeekStartDay.SUNDAY,
        )
        assert settings.language == LanguageCode("ru")
        assert settings.timezone == Timezone("Europe/Moscow")
        assert settings.date_format == DateFormat("DD.MM.YYYY")

    def test_frozen(self) -> None:
        settings = LocalizationSettings()
        with pytest.raises(Exception):
            settings.language = LanguageCode("de")

    def test_equality_by_value(self) -> None:
        s1 = LocalizationSettings()
        s2 = LocalizationSettings()
        assert s1 == s2
