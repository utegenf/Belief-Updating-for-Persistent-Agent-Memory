from belief_memory import SourceAwareMemory
from belief_memory.models import FunctionalType
from belief_memory.router import CallableRouter, RouteResult

def test_router_receives_content_not_source():
    seen = {}
    def classify(content):
        seen["content"] = content
        return RouteResult(FunctionalType.PERSONAL_PREFERENCE, summarized_content=content)
    memory = SourceAwareMemory(trusted_sources={"user"}, router=CallableRouter(classify))
    memory.observe("I prefer tea.", source="document")
    memory.consolidate()
    assert seen == {"content": "I prefer tea."}
    assert memory.beliefs() == []
