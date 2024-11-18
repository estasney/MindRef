from typing import Protocol, TypeVar, Deque, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.domain.protocols import AppRegistryProtocol

T = TypeVar("T")


class NotificationRepository(Protocol[T]):
    """
    Abstract Protocol for a Service that handles the creation and displaying of Notifications
    """

    notifications: Deque[T]
    get_app: Callable[[], "AppRegistryProtocol"]
    current_notification: Optional[str]

    def add_notification(self, notification: T) -> None:
        """
        Add a Notification to the notifications deque
        """
        ...

    def next_notification(self) -> Optional[T]:
        """
        Return the next Notification in the notifications deque
        """
        ...

    def remove_notification(self, notification_id: str) -> None:
        """
        Remove a Notification from the notifications deque
        """
        ...
