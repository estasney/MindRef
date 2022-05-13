from typing import Sequence, Union

from .protocol import DottedList, Publisher
from .topic import Topic, TopicCollection


class Registry:
    """
    Registry class that manages several topics

    Examples
    --------
    ```python
    r = Registry("my_registry")
    my_topic = r.add_topic("my_topic")

    @my_topic
    def run_on_my_topic(*args, **kwargs):
        print("my_topic was just run!")


    r.my_topic.notify()

    ```

    """

    topics = TopicCollection()

    def __init__(self, namespace: str):
        self.namespace = namespace

    def __contains__(self, item: str):
        return item in self.topic_names

    def __call__(self, *args, **kwargs):
        ...

    def __getattr__(self, item):
        return getattr(self.topics, item)

    @property
    def topic_names(self) -> list[str]:
        return [top.name for top in self.topics]

    def add_topic(self, topic_name: str) -> Topic:
        if topic_name in self:
            raise ValueError(f"{topic_name} is already present in {self!r}.topics")
        topic_obj = Topic(topic_name)
        self.topics = [*self.topics, topic_obj]
        return topic_obj

    def add_topics(self, topic_names: Sequence[str]) -> list[Topic]:
        seen = set()
        errs = []
        for topic_name in topic_names:
            if topic_name in seen:
                errs.append(f"{topic_name} is duplicated")
                continue
            elif topic_name in self:
                errs.append(f"{topic_name} already exists in {self!r}.topics")
                continue
            seen.add(topic_name)
        if errs:
            raise ValueError(f"Duplicate topics : {','.join(errs)}")
        del errs
        topic_objs = [Topic(name) for name in topic_names]
        self.topics = [*self.topics, *topic_objs]
        return topic_objs

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
