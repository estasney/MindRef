import functools

import pytest
from kvnoteafly.registry import Registry


@pytest.fixture()
def base_registry():
    reg = Registry("testapp")
    yield reg



@pytest.fixture()
def registry_topic(base_registry):
    topic = base_registry.add_topic('testtopic')
    yield base_registry, topic
    base_registry.remove_topic('testtopic')


@pytest.fixture()
def wrapped_func(registry_topic):

    def _wrapped_func(func, emitter, listener):
        registry, topic = registry_topic
        topic.set_emitter(emitter)
        topic.add_listener(listener)
        return registry.topics('testtopic')(func)

    return _wrapped_func
