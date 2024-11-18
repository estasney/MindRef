from collections import deque

from kivy.properties import Logger

from .notification_repository import NotificationRepository
from ...domain.events import NotificationEvent
from ...utils import sch_cb, schedulable
from ...widgets.toast.toast import Toast


class NotificationService(NotificationRepository):
    def __init__(self, get_app):
        self.get_app = get_app
        self.notifications = deque()
        self.current_notification = None

    def add_notification(self, notification: NotificationEvent):
        if notification not in self.notifications:
            self.notifications.append(notification)
            sch_cb(self.process_notifications, timeout=0.1)

    def next_notification(self) -> NotificationEvent:
        return self.notifications.popleft()

    def remove_notification(self, notification_id: str):
        try:
            matched_index = self.notifications.index(notification_id)
            self.notifications.rotate(-matched_index)
            self.notifications.popleft()
            self.notifications.rotate(matched_index)
        except ValueError:
            return

    def process_notifications(self, *args):
        Logger.info(f"Processing Notifications: {self.notifications}")
        if self.current_notification is None:
            next_notification = self.next_notification()
            if not next_notification:
                return
            self.current_notification = next_notification.id
            Toast.show_toast(
                title=next_notification.title,
                text=next_notification.message,
                duration=5000,
                on_close=self.remove_notification,
            )
