import pytest


@pytest.mark.registry
def test_registry_init(base_registry):
    """
    Given newly created registry
    Check that topic_names and topics are empty lists
    """
    assert base_registry.topic_names == []
    assert base_registry.topics == []


@pytest.mark.registry
def test_registry_topics(registry_topic):
    """
    Given a registry and a topic
    Define a listener function that will modify a variable
    Call `topic.notify` and check that the listener function was run
    """
    registry, topic = registry_topic

    g_object = None

    @topic
    def listener(*args, **kwargs):
        nonlocal g_object
        g_object = args[0]

    topic.notify(5)
    assert g_object == 5

    registry.testtopic.notify(10)
    assert g_object == 10


@pytest.mark.registry
def test_get_topic(registry_topic):
    registry, topic = registry_topic
    assert registry.get_topic(top=topic.name) == topic


@pytest.mark.registry
def test_registry_dynamic_listeners(registry_topic):
    """
    Given a registry, topic and several listeners
    Subscribe all listeners
    Remove listeners, ensuring their callbacks are not invoked

    Parameters
    ----------
    registry_topic

    Returns
    -------

    """
    registry, topic = registry_topic

    g_object = []

    class MultiListener:
        def __init__(self, x):
            self.x = x
            topic(self.topic_listener)

        def topic_listener(self):
            nonlocal g_object
            g_object.append(self.x)

    assert len(g_object) == 0
    x1 = MultiListener(1)
    x10 = MultiListener(10)
    topic.notify()
    assert 10 in g_object
    assert 1 in g_object
    g_object.clear()
    topic.remove_listener(x10.topic_listener)
    del x10
    topic.notify()
    assert 10 not in g_object
    assert 1 in g_object
    g_object.clear()
    topic.remove_listener(x1.topic_listener)
    del x1
    topic.notify()
    assert len(g_object) == 0


@pytest.mark.registry
def test_dotted_registry(registry_topic):
    registry, topic = registry_topic
    assert getattr(registry.topics, topic.name) == topic
    assert getattr(registry, topic.name) == topic


@pytest.mark.registry
def test_duplicated_topics(registry_topic):
    registry, topic = registry_topic
    with pytest.raises(ValueError):
        registry.add_topic(topic.name)
    with pytest.raises(ValueError):
        registry.add_topics(["New", topic.name])
    with pytest.raises(ValueError):
        registry.add_topics(["One", "One", "Two"])
