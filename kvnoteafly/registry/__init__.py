from typing import Union

from .protocol import DottedList, Publisher
from .topic import Topic, TopicCollection


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
        return [top.name for top in self.topics]

    def add_topic(self, topic_name: str) -> Topic:
        topic_obj = Topic(topic_name)
        self.topics = [*self.topics, topic_obj]
        return topic_obj

    def get_topic(self, top: Union[str, Topic]) -> Topic:
        key = top.name if isinstance(top, Topic) else top
        matched_topic = next((t for t in self.topics if t.name == key), None)
        if not matched_topic:
            raise KeyError(f"{top} not in {self.topics}")
        return matched_topic

    def remove_topic(self, topic_name: str) -> Topic:
        topics = [top for top in self.topics]
        matched_topic = next((t for t in self.topics if t.name == topic_name), None)
        if not matched_topic:
            raise KeyError(f"{topic_name} not in {self}.topics")
        topics.remove(matched_topic)
        self.topics = topics
        return matched_topic
