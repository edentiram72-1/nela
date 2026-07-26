"""Safe browser and web-search Agent for NELA."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import re
from typing import Protocol
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen
import webbrowser

from agents.base import AgentCommand, AgentResult, BaseAgent
from permissions.models import AgentManifest, Capability, PermissionTier


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


class BrowserOpener(Protocol):
    def open(self, url: str) -> bool:
        """Open a URL in the user's browser."""


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int, timeout_seconds: float) -> tuple[SearchResult, ...]:
        """Search the web and return normalized results."""


class SystemBrowserOpener:
    def open(self, url: str) -> bool:
        return webbrowser.open(url, new=2, autoraise=True)


class DuckDuckGoSearchProvider:
    """Small stdlib-only search provider.

    This is intentionally conservative: one approved provider, no scripting, no
    cookies, and normalized text output only.
    """

    endpoint = "https://duckduckgo.com/html/"

    def search(self, query: str, max_results: int, timeout_seconds: float) -> tuple[SearchResult, ...]:
        url = f"{self.endpoint}?q={quote_plus(query)}"
        request = Request(
            url,
            headers={
                "User-Agent": "NELA-OS/0.1 defensive-search",
                "Accept": "text/html",
            },
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read(500_000).decode("utf-8", errors="replace")
        return _parse_duckduckgo_html(html, max_results=max_results)


class BrowserAgent(BaseAgent):
    """Opens safe URLs and performs bounded web searches."""

    name = "browser"
    permission_manifest = AgentManifest(
        agent="browser",
        capabilities=(
            Capability("describe_capabilities", PermissionTier.T0, "Describe Browser Agent capabilities.", actions=("describe_capabilities",)),
            Capability("browser.url.open", PermissionTier.T1, "Open an http/https URL in the local browser.", actions=("open_url",)),
            Capability("browser.search.web", PermissionTier.T1, "Search the web through an approved provider.", actions=("search_web", "prepare_search")),
            Capability("browser.results.filter", PermissionTier.T0, "Filter supplied search results.", actions=("filter_results",)),
        ),
    )

    def __init__(
        self,
        opener: BrowserOpener | None = None,
        search_provider: SearchProvider | None = None,
    ) -> None:
        super().__init__()
        self._opener = opener or SystemBrowserOpener()
        self._search_provider = search_provider or DuckDuckGoSearchProvider()

    def execute(self, command: AgentCommand) -> AgentResult:
        if command.action == "describe_capabilities":
            return AgentResult(
                True,
                "Browser Agent can prepare/search/filter safe web results and open approved URLs.",
                {
                    "agent": self.name,
                    "supported_actions": ("open_url", "prepare_search", "search_web", "filter_results"),
                    "safety": "approved_search_and_safe_url_open_only",
                },
            )
        if command.action == "open_url":
            return self._open_url(command)
        if command.action == "prepare_search":
            return self._prepare_search(command)
        if command.action == "search_web":
            return self._search_web(command)
        if command.action == "filter_results":
            return self._filter_results(command)
        return AgentResult(
            False,
            "Unsupported browser action.",
            {
                "agent": self.name,
                "supported_actions": ("open_url", "prepare_search", "search_web", "filter_results"),
            },
        )

    def health_check(self) -> AgentResult:
        result = super().health_check()
        return AgentResult(
            result.success,
            result.message,
            {
                **result.data,
                "provider": "duckduckgo_html",
                "safety": "approved_search_and_safe_url_open_only",
            },
        )

    def _open_url(self, command: AgentCommand) -> AgentResult:
        url = _safe_url(str(command.payload.get("url") or command.payload.get("resource") or "https://www.google.com"))
        if url is None:
            return AgentResult(False, "URL is not allowed.", {"agent": self.name, "reason": "invalid_or_unsafe_url"})
        opened = self._opener.open(url)
        return AgentResult(
            opened,
            f"Opened {url}." if opened else f"Could not open {url}.",
            {
                "agent": self.name,
                "url": url,
                "opened": opened,
            },
        )

    def _prepare_search(self, command: AgentCommand) -> AgentResult:
        query = _clean_query(str(command.payload.get("query") or command.payload.get("text") or ""))
        unsafe_reason = _unsafe_query_reason(query)
        if unsafe_reason:
            return _unsafe_result(self.name, unsafe_reason, query)
        search_url = _search_url(query)
        return AgentResult(
            True,
            f"Prepared web search for {query}.",
            {
                "agent": self.name,
                "query": query,
                "search_url": search_url,
                "work_product": _work_product(
                    summary="Search prepared.",
                    results=(SearchResult("קישור חיפוש מוכן", search_url, "אפשר לפתוח את החיפוש או לבקש ממני לסנן תוצאות."),),
                    next_steps=("לפתוח את החיפוש בדפדפן או להריץ חיפוש חי דרך ספק מאושר.",),
                ),
            },
        )

    def _search_web(self, command: AgentCommand) -> AgentResult:
        query = _clean_query(str(command.payload.get("query") or command.payload.get("text") or ""))
        unsafe_reason = _unsafe_query_reason(query)
        if unsafe_reason:
            return _unsafe_result(self.name, unsafe_reason, query)
        max_results = _bounded_int(command.payload.get("max_results"), default=5, lower=1, upper=8)
        timeout_seconds = float(command.payload.get("timeout_seconds") or 10.0)
        include_terms = _as_terms(command.payload.get("include_terms"))
        exclude_terms = _as_terms(command.payload.get("exclude_terms"))
        try:
            results = self._search_provider.search(query, max_results=max_results * 2, timeout_seconds=timeout_seconds)
        except Exception as error:
            search_url = _search_url(query)
            fallback = SearchResult("החיפוש החי לא הושלם", search_url, f"אפשר לפתוח את החיפוש בדפדפן. שגיאה: {error.__class__.__name__}")
            return AgentResult(
                True,
                "Live search failed; prepared a browser search URL instead.",
                {
                    "agent": self.name,
                    "query": query,
                    "search_url": search_url,
                    "results": [fallback.to_dict()],
                    "work_product": _work_product(
                        summary="Search fallback prepared.",
                        results=(fallback,),
                        next_steps=("לפתוח את קישור החיפוש או לנסות שוב מאוחר יותר.",),
                    ),
                },
            )
        if not results:
            search_url = _search_url(query)
            fallback = SearchResult("קישור חיפוש מוכן", search_url, "לא הצלחתי לפענח תוצאות חיות, אבל הכנתי חיפוש לפתיחה בדפדפן.")
            return AgentResult(
                True,
                "No parsed live results; prepared a browser search URL instead.",
                {
                    "agent": self.name,
                    "query": query,
                    "search_url": search_url,
                    "results": [fallback.to_dict()],
                    "results_count": 1,
                    "work_product": _work_product(
                        summary="Search fallback prepared.",
                        results=(fallback,),
                        next_steps=("לפתוח את קישור החיפוש או לדייק את השאילתה.",),
                    ),
                },
            )
        filtered = _filter_results(results, include_terms=include_terms, exclude_terms=exclude_terms)[:max_results]
        if not filtered:
            search_url = _search_url(query)
            fallback = SearchResult("קישור חיפוש אחרי סינון", search_url, "הסינון לא השאיר תוצאות, אז שמרתי את החיפוש המקורי לפתיחה.")
            filtered = (fallback,)
        return AgentResult(
            True,
            f"Found {len(filtered)} filtered result(s) for {query}.",
            {
                "agent": self.name,
                "query": query,
                "search_url": _search_url(query),
                "results": [result.to_dict() for result in filtered],
                "results_count": len(filtered),
                "work_product": _work_product(
                    summary=f"Web search completed for {query}.",
                    results=filtered,
                    next_steps=("לפתוח תוצאה ספציפית רק אם היא נראית רלוונטית ובטוחה.",),
                ),
            },
        )

    def _filter_results(self, command: AgentCommand) -> AgentResult:
        raw_results = command.payload.get("results") or ()
        results = tuple(
            SearchResult(
                title=str(item.get("title", "")),
                url=str(item.get("url", "")),
                snippet=str(item.get("snippet", "")),
            )
            for item in raw_results
            if isinstance(item, dict)
        )
        filtered = _filter_results(
            results,
            include_terms=_as_terms(command.payload.get("include_terms")),
            exclude_terms=_as_terms(command.payload.get("exclude_terms")),
        )
        return AgentResult(
            True,
            f"Filtered {len(filtered)} result(s).",
            {
                "agent": self.name,
                "results": [result.to_dict() for result in filtered],
                "results_count": len(filtered),
                "work_product": _work_product(
                    summary="Search results filtered.",
                    results=filtered,
                    next_steps=("לבחור תוצאה לפתיחה או לדייק את החיפוש.",),
                ),
            },
        )


def _safe_url(raw: str) -> str | None:
    value = raw.strip()
    if not value:
        return None
    initial = urlparse(value)
    if initial.scheme and initial.scheme.lower() not in {"http", "https"}:
        return None
    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = f"https://{value}"
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if parsed.username or parsed.password:
        return None
    return value


def _clean_query(raw: str) -> str:
    query = " ".join(raw.strip().split())
    prefixes = (
        "נלה",
        "חפשי באינטרנט",
        "תחפשי באינטרנט",
        "חפשי ברשת",
        "תחפשי ברשת",
        "חפשי בגוגל",
        "תחפשי בגוגל",
        "חפשי",
        "תחפשי",
        "search web for",
        "search for",
        "look up",
        "google",
    )
    lowered = query.lower()
    for prefix in prefixes:
        normalized = prefix.lower()
        if lowered.startswith(normalized):
            query = query[len(prefix):].strip(" :,-")
            break
    return _remove_filter_clauses(query)


def _unsafe_query_reason(query: str) -> str | None:
    lowered = query.lower()
    blocked = (
        "לעקוף",
        "תעקפי",
        "bypass",
        "credential theft",
        "steal password",
        "phishing",
        "malware",
        "ransomware",
        "ddos",
        "exploit payload",
    )
    if not query:
        return "empty_query"
    if any(term in lowered for term in blocked):
        return "unsafe_query"
    return None


def _remove_filter_clauses(text: str) -> str:
    cleaned = text
    for marker in ("בלי", "ללא", "exclude", "רק", "include"):
        cleaned = re.sub(rf"(?:^|\s){re.escape(marker)}\s+[^,.;]+", " ", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split())


def _unsafe_result(agent: str, reason: str, query: str) -> AgentResult:
    return AgentResult(
        False,
        "Search request is outside safe browsing scope.",
        {
            "agent": agent,
            "query": query,
            "reason": reason,
            "safe_alternative": "אפשר לחפש הסבר הגנתי, תיעוד רשמי, או דרך חוקית לקבל הרשאה.",
        },
    )


def _search_url(query: str) -> str:
    return f"https://duckduckgo.com/?q={quote_plus(query)}"


def _parse_duckduckgo_html(html: str, max_results: int) -> tuple[SearchResult, ...]:
    results: list[SearchResult] = []
    pattern = re.compile(
        r'class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html):
        title = _strip_html(match.group("title"))
        url = unescape(match.group("url"))
        snippet = _strip_html(match.group("snippet"))
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= max_results:
            break
    if results:
        return tuple(results)

    title_pattern = re.compile(r'class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>', re.IGNORECASE | re.DOTALL)
    for match in title_pattern.finditer(html):
        title = _strip_html(match.group("title"))
        url = unescape(match.group("url"))
        if title and url:
            results.append(SearchResult(title=title, url=url))
        if len(results) >= max_results:
            break
    return tuple(results)


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(text).split())


def _bounded_int(value: object, default: int, lower: int, upper: int) -> int:
    try:
        parsed = int(value) if value is not None else default
    except (TypeError, ValueError):
        parsed = default
    return max(lower, min(upper, parsed))


def _as_terms(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(term.strip().lower() for term in value.split(",") if term.strip())
    if isinstance(value, (list, tuple, set)):
        return tuple(str(term).strip().lower() for term in value if str(term).strip())
    return ()


def _filter_results(
    results: tuple[SearchResult, ...],
    include_terms: tuple[str, ...] = (),
    exclude_terms: tuple[str, ...] = (),
) -> tuple[SearchResult, ...]:
    filtered: list[SearchResult] = []
    for result in results:
        haystack = f"{result.title} {result.url} {result.snippet}".lower()
        if include_terms and not all(term in haystack for term in include_terms):
            continue
        if exclude_terms and any(term in haystack for term in exclude_terms):
            continue
        filtered.append(result)
    return tuple(filtered)


def _work_product(
    summary: str,
    results: tuple[SearchResult, ...],
    next_steps: tuple[str, ...],
) -> dict[str, object]:
    findings = [
        {
            "title": result.title,
            "severity": "info",
            "category": "web_result",
            "location": result.url,
            "evidence": result.snippet,
            "recommendation": "לפתוח רק אם המקור נראה אמין ורלוונטי.",
        }
        for result in results
    ]
    return {
        "summary": summary,
        "findings": findings,
        "artifacts": [
            {
                "kind": "search_results",
                "name": "browser.search_results",
                "content": "\n".join(f"{index}. {item.title} - {item.url}" for index, item in enumerate(results, start=1)),
                "metadata": {},
            }
        ],
        "next_steps": list(next_steps),
    }
