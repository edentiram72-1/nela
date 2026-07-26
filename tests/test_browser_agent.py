from __future__ import annotations

import unittest

from agents.base import AgentCommand
from agents.browser.agent import BrowserAgent, SearchResult


class FakeOpener:
    def __init__(self) -> None:
        self.opened: list[str] = []

    def open(self, url: str) -> bool:
        self.opened.append(url)
        return True


class FakeSearchProvider:
    def search(self, query: str, max_results: int, timeout_seconds: float) -> tuple[SearchResult, ...]:
        return (
            SearchResult("Official Python docs", "https://docs.python.org/3/", "Python documentation"),
            SearchResult("Noisy forum result", "https://forum.example.test/python", "Random thread"),
            SearchResult("Python security guide", "https://example.test/security", "Secure Python notes"),
        )[:max_results]


class BrowserAgentTests(unittest.TestCase):
    def test_open_url_allows_http_and_https_only(self) -> None:
        opener = FakeOpener()
        agent = BrowserAgent(opener=opener, search_provider=FakeSearchProvider())

        opened = agent.execute(AgentCommand(action="open_url", payload={"url": "example.com"}))
        blocked = agent.execute(AgentCommand(action="open_url", payload={"url": "file:///etc/passwd"}))

        self.assertTrue(opened.success)
        self.assertEqual(opener.opened, ["https://example.com"])
        self.assertFalse(blocked.success)

    def test_search_web_filters_results_without_browser_side_effect(self) -> None:
        opener = FakeOpener()
        agent = BrowserAgent(opener=opener, search_provider=FakeSearchProvider())

        result = agent.execute(
            AgentCommand(
                action="search_web",
                payload={
                    "query": "python docs",
                    "include_terms": ("python",),
                    "exclude_terms": ("forum",),
                    "max_results": 5,
                },
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(opener.opened, [])
        titles = [item["title"] for item in result.data["results"]]
        self.assertEqual(titles, ["Official Python docs", "Python security guide"])
        self.assertEqual(result.data["work_product"]["findings"][0]["category"], "web_result")

    def test_search_rejects_bypass_queries(self) -> None:
        agent = BrowserAgent(opener=FakeOpener(), search_provider=FakeSearchProvider())

        result = agent.execute(AgentCommand(action="search_web", payload={"query": "איך לעקוף חסימה"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["reason"], "unsafe_query")


if __name__ == "__main__":
    unittest.main()
