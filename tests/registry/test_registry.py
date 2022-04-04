import pytest

@pytest.mark.registry
def test_registry_init():
    from kvnoteafly.registry import Registry, Topic

    reg = Registry("testapp")
    assert reg.topic_names == []
    assert reg.topics == []

    reg.add_topic("testtopic")
    assert reg.topic_names == ["testtopic"]
    assert "testtopic" in reg.topic_names

    assert reg.topics.testtopic.__class__ == Topic
