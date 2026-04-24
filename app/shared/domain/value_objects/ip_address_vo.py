from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class IpAddress(ValueObject):
    """
    Value Object для IP-адреса.

    Гарантирует, что значение является валидным IPv4 или IPv6 адресом.

    Атрибуты:
        value: Строковое представление IP-адреса.

    Пример:
        ip = IpAddress("192.168.1.1")
        ip6 = IpAddress("::1")
    """

    value: str

    def __post_init__(self) -> None:
        try:
            ipaddress.ip_address(self.value)
        except ValueError:
            raise ValidationException(
                field="ip_address",
                message=f"Некорректный IP-адрес: {self.value}",
            )

    @property
    def is_ipv4(self) -> bool:
        return isinstance(ipaddress.ip_address(self.value), ipaddress.IPv4Address)

    @property
    def is_ipv6(self) -> bool:
        return isinstance(ipaddress.ip_address(self.value), ipaddress.IPv6Address)

    def __str__(self) -> str:
        return self.value
