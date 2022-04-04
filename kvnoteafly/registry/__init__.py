from collections import UserList
from typing import Any, Optional, Callable


class Topic:
    def __init__(self, name: str):
        self.name = name
        self.listeners = []

    def notify(self):
        for listener in self.listeners:
            listener()

    def add_listener(self, cb: Callable):
        self.listeners.append(cb)


class DottedList(UserList):

    def __init__(self, initlist=None, key_name: str = "name"):
        super().__init__(initlist)
        self.key_name = key_name

    def __getattr__(self, name: str):
        try:
            return next((item for item in self.data if getattr(item, self.key_name) == name))
        except StopIteration:
            raise AttributeError(f"{name} does not exist")


class TopicCollection:

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        self.wrapper_name = f"{self.private_name}_wrapper"
        setattr(owner, f"_{name}_wrapper", DottedList())

    def __get__(self, obj, objtype=None) -> list:
        result = getattr(obj, self.wrapper_name)
        return result

    def __set__(self, obj, value):
        if not value:
            setattr(obj, self.wrapper_name, DottedList())
        else:
            setattr(obj, self.wrapper_name, DottedList(value))


class Registry:
    topics = TopicCollection()

    def __init__(self, namespace: str):
        self.namespace = namespace

    def __contains__(self, item: str):
        return item in self.topic_names

    def __call__(self, *args, **kwargs):
        ...

    @property
    def topic_names(self) -> list[str]:
        return [topic.name for topic in self.topics]

    def add_topic(self, topic_name: str):
        self.topics = [*self.topics, Topic(topic_name)]

#
# class Registry:
#     def __init__(self, topic: str):
#         self.topic = topic
#
#     def add_topic(self, topic: str) -> "Topic":
#         topic_obj = Topic(topic)
#         self.topics[topic] = topic_obj
#         return topic_obj
#
#     def get_topic(self, topic: str) -> "Topic":
#         return self.topics[topic]
#
#     def on(self, topic: str, *, func: Optional[Any] = None):
#
#         def _attach(inner_func):
#             topic_obj = self.topics.get(topic)
#             if not topic_obj:
#                 topic_obj = self.add_topic(topic)
#             topic_obj.add_listener(inner_func)
#             return inner_func
#
#         if func is not None:
#             return _attach(func)
#         return _attach
