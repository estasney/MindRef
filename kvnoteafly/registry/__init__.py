from typing import Any, Optional


class Topic:
    def __init__(self, topic: str):
        self.topic = topic
        self.listeners = []

    def notify(self):
        for listener in self.listeners:
            listener()

    def add_listener(self, cb: callable):
        self.listeners.append(cb)


class Registry:
    def __init__(self):
        self.topics = {}

    def add_topic(self, topic: str) -> "Topic":
        topic_obj = Topic(topic)
        self.topics[topic] = topic_obj
        return topic_obj

    def get_topic(self, topic: str) -> "Topic":
        return self.topics[topic]

    def on(self, topic: str, *, func: Optional[Any] = None):

        def _attach(inner_func):
            topic_obj = self.topics.get(topic)
            if not topic_obj:
                topic_obj = self.add_topic(topic)
            topic_obj.add_listener(inner_func)
            return inner_func

        if func is not None:
            return _attach(func)
        return _attach
