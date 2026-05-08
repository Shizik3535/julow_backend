from __future__ import annotations


def changed_fields(old_vo: object, new_vo: object) -> list[str]:
    """
    Вычисляет список имён изменённых полей между двумя VO-группами.

    Обе записи должны быть dataclass-экземплярами одного типа.

    Аргументы:
        old_vo: Старое значение VO.
        new_vo: Новое значение VO.

    Возвращает:
        Список имён полей, значения которых различаются.
    """
    changed: list[str] = []
    for f_name in type(old_vo).__dataclass_fields__:
        if getattr(old_vo, f_name) != getattr(new_vo, f_name):
            changed.append(f_name)
    return changed
