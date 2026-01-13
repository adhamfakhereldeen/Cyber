from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="SerializableMixin")


class SerializableMixin:
    """Provide JSON-serializable helpers."""

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)  # type: ignore[arg-type]


class AuditableMixin:
    """Provide simple audit helper that delegates to audit logger."""

    def audit(self, event_type: str, details: str, actor: str = "system") -> None:
        try:
            from core.logger import audit_log
        except ImportError:
            # Fallback import for relative path when running as package
            from ..core.logger import audit_log  # type: ignore

        audit_log(event_type=event_type, actor=actor, details=details)
