import pytest


@pytest.mark.registry
def test_registry_init(base_registry):
    assert base_registry.topic_names == []
    assert base_registry.topics == []


@pytest.mark.registry
def test_registry_topics(registry_topic):
    registry, topic = registry_topic

    g_object = None

    def emitter(listeners, result):
        nonlocal g_object
        for listener_f in listeners:
            g_object = listener_f(result)

    def listener(x):
        return x

    topic.set_emitter(emitter)
    topic.add_listener(listener)
    topic.notify(5)
    assert g_object == 5


@pytest.mark.registry
def test_registry_decorators(wrapped_func):
    g_object = None

    def emitter(listeners, result):
        nonlocal g_object
        for listener_f in listeners:
            g_object = listener_f(result)

    def listener(x):
        return x

    def decorated_function():
        return 1

    wrapped_func(decorated_function, emitter, listener)()
    assert g_object == 1


def test_get_topic(registry_topic):
    registry, topic = registry_topic
    assert registry.get_topic(top=topic.name) == topic
