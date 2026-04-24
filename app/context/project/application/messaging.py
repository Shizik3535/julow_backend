from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectMessagingConfig:
    """
    Конфигурация messaging для Project BC.

    Публикация:
        - Топик: project.events

    Подписки:
        - workspace.events → OnWorkspaceMemberRemoved (consumer group: project-bc)
        - project.events → OnAutomationRuleTriggered (consumer group: project-bc)
    """

    publish_topic: str = "project.events"
    subscriptions: list[dict[str, str]] = field(default_factory=lambda: [
        {
            "topic": "workspace.events",
            "handler": "OnWorkspaceMemberRemoved",
            "consumer_group": "project-bc",
        },
        {
            "topic": "project.events",
            "handler": "OnAutomationRuleTriggered",
            "consumer_group": "project-bc",
        },
    ])
