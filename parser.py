"""
Модуль парсинга новостей об Эпштейне из множества источников.
Использует xml.etree для парсинга RSS (без зависимости от feedparser).
"""

import json
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

import config


@dataclass
class Article:
    title: str
    url: str
    source: str
    published: Optional[datetime] = None
    summary: str = ""
    relevance_score: int = 0
    keywords_found: list = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        if self.published:
            d["published"] = self.published.isoformat()
        return d


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def _normalize_url(url: str) -> str:
    """Убираем query-параметры трекинга для дедупликации."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def _load_seen_urls() -> set:
    path = Path(config.SEEN_URLS_FILE)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def _save_seen_urls(seen: set):
    with open(config.SEEN_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def _score_article(title: str, summary: str) -> tuple[int, list]:
    """Оценка релевантности по ключевым словам."""
    text = f"{title} {summary}".lower()
    found = []
    for kw in config.KEYWORDS:
        if kw.lower() in text:
            found.append(kw)
    return len(found), found


def _parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return dateparser.parse(date_str)
    except (ValueError, OverflowError):
        return None


def _fetch(url: str, timeout: int = None) -> Optional[str]:
    """GET-запрос с обработкой ошибок."""
    timeout = timeout or config.REQUEST_TIMEOUT
    try:
        resp = requests.get(
            url,
            headers=config.REQUEST_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        print(f"  [!] Ошибка загрузки {url}: {exc}")
        return None


def _strip_html(text: str) -> str:
    """Убираем HTML-теги из текста."""
    if not text:
        return ""
    return BeautifulSoup(text, "lxml").get_text(separator=" ", strip=True)


# ---------------------------------------------------------------------------
# RSS-парсер на xml.etree (замена feedparser)
# ---------------------------------------------------------------------------

def _parse_rss_xml(xml_text: str) -> list[dict]:
    """Парсим RSS/Atom XML и возвращаем список записей."""
    entries = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return entries

    # Определяем namespace для Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # Попытка 1: RSS 2.0 (<rss><channel><item>)
    channel = root.find("channel")
    if channel is not None:
        feed_title = _xml_text(channel, "title")
        for item in channel.findall("item"):
            entries.append({
                "title": _xml_text(item, "title"),
                "link": _xml_text(item, "link"),
                "summary": _xml_text(item, "description"),
                "published": _xml_text(item, "pubDate"),
                "feed_title": feed_title,
                "source": _xml_text(item, "source"),
            })
        return entries

    # Попытка 2: Atom (<feed><entry>)
    feed_title = ""
    title_el = root.find("atom:title", ns) or root.find("title")
    if title_el is not None:
        feed_title = title_el.text or ""

    for entry in root.findall("atom:entry", ns) + root.findall("entry"):
        title = ""
        title_el = entry.find("atom:title", ns) or entry.find("title")
        if title_el is not None:
            title = title_el.text or ""

        link = ""
        link_el = entry.find("atom:link", ns) or entry.find("link")
        if link_el is not None:
            link = link_el.get("href", "") or (link_el.text or "")

        summary = ""
        for tag in ["atom:summary", "atom:content"]:
            s_el = entry.find(tag, ns)
            if s_el is not None and s_el.text:
                summary = s_el.text
                break
        if not summary:
            for tag in ["summary", "content"]:
                s_el = entry.find(tag)
                if s_el is not None and s_el.text:
                    summary = s_el.text
                    break

        published = ""
        for tag in ["atom:published", "atom:updated"]:
            p_el = entry.find(tag, ns)
            if p_el is not None and p_el.text:
                published = p_el.text
                break
        if not published:
            for tag in ["published", "updated"]:
                p_el = entry.find(tag)
                if p_el is not None and p_el.text:
                    published = p_el.text
                    break

        entries.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "feed_title": feed_title,
            "source": "",
        })

    return entries


def _xml_text(parent, tag: str) -> str:
    """Безопасное извлечение текста из XML-элемента."""
    el = parent.find(tag)
    if el is not None and el.text:
        return el.text.strip()
    return ""


# ---------------------------------------------------------------------------
# Парсеры источников
# ---------------------------------------------------------------------------

def parse_rss_feeds() -> list[Article]:
    """Парсим все RSS-фиды из конфига."""
    articles = []
    for feed_url in config.RSS_FEEDS:
        print(f"  [RSS] {feed_url}")
        xml_text = _fetch(feed_url)
        if not xml_text:
            continue

        entries = _parse_rss_xml(xml_text)
        for entry in entries:
            title = entry["title"]
            link = entry["link"]
            summary = _strip_html(entry["summary"])

            score, kws = _score_article(title, summary)
            if score >= config.MIN_KEYWORD_MATCHES:
                pub_date = _parse_date(entry["published"])
                source_name = entry["feed_title"] or urlparse(feed_url).netloc
                articles.append(Article(
                    title=title.strip(),
                    url=link.strip(),
                    source=source_name,
                    published=pub_date,
                    summary=summary[:500],
                    relevance_score=score,
                    keywords_found=kws,
                ))
        time.sleep(0.3)
    return articles


def parse_google_news_rss() -> list[Article]:
    """Парсим Google News RSS-поиск."""
    articles = []
    for src in config.SCRAPE_SOURCES:
        if src["type"] != "google_news_rss":
            continue
        print(f"  [Google News RSS] {src['name']}")
        xml_text = _fetch(src["url"])
        if not xml_text:
            continue

        entries = _parse_rss_xml(xml_text)
        for entry in entries:
            title = entry["title"]
            link = entry["link"]
            summary = _strip_html(entry["summary"])

            score, kws = _score_article(title, summary)
            pub_date = _parse_date(entry["published"])
            source_name = entry["source"] or src["name"]

            articles.append(Article(
                title=title.strip(),
                url=link.strip(),
                source=source_name,
                published=pub_date,
                summary=summary[:500],
                relevance_score=max(score, 1),
                keywords_found=kws or ["epstein"],
            ))
        time.sleep(0.5)
    return articles


def parse_courtlistener() -> list[Article]:
    """Парсим CourtListener — судебные документы."""
    articles = []
    for src in config.SCRAPE_SOURCES:
        if src["type"] != "courtlistener":
            continue
        print(f"  [CourtListener] {src['name']}")
        html = _fetch(src["url"])
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        results = soup.select("article.v-list-item, .search-result, .result-title")

        for item in results[:15]:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            title = link_tag.get_text(strip=True)
            href = link_tag["href"]
            if not href.startswith("http"):
                href = f"https://www.courtlistener.com{href}"

            snippet_tag = item.find(class_="description") or item.find("p")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

            score, kws = _score_article(title, snippet)
            articles.append(Article(
                title=title,
                url=href,
                source="CourtListener",
                summary=snippet[:500],
                relevance_score=max(score, 1),
                keywords_found=kws or ["epstein"],
            ))
    return articles


# ---------------------------------------------------------------------------
# Главная функция сбора
# ---------------------------------------------------------------------------

def _is_fresh(article: Article, max_age_hours: int) -> bool:
    """Проверяем, что статья не старше max_age_hours часов."""
    if not article.published:
        # Без даты — пропускаем (не можем гарантировать свежесть)
        return False
    now = datetime.now(timezone.utc)
    pub = article.published
    # Если дата naive — считаем UTC
    if pub.tzinfo is None:
        pub = pub.replace(tzinfo=timezone.utc)
    age = now - pub
    return age <= timedelta(hours=max_age_hours)


def collect_all(skip_seen: bool = True, max_age_hours: int = None) -> list[Article]:
    """Собираем новости из всех источников, фильтруем по свежести, дедуплицируем."""
    if max_age_hours is None:
        max_age_hours = config.MAX_AGE_HOURS

    seen = _load_seen_urls() if skip_seen else set()
    all_articles: list[Article] = []

    print("\n=== Сбор новостей об Эпштейне ===\n")
    print(f"    Фильтр: только за последние {max_age_hours}ч\n")

    # 1. RSS-фиды
    print("[1/3] RSS-фиды крупных СМИ...")
    all_articles.extend(parse_rss_feeds())

    # 2. Google News RSS
    print("\n[2/3] Google News RSS...")
    all_articles.extend(parse_google_news_rss())

    # 3. CourtListener
    print("\n[3/3] CourtListener (судебные документы)...")
    all_articles.extend(parse_courtlistener())

    # Фильтр по свежести
    fresh = [a for a in all_articles if _is_fresh(a, max_age_hours)]
    stale_count = len(all_articles) - len(fresh)
    if stale_count:
        print(f"\n  Отфильтровано старых статей: {stale_count}")

    # Дедупликация
    unique: dict[str, Article] = {}
    for art in fresh:
        norm = _normalize_url(art.url)
        if norm in seen:
            continue
        if norm in unique:
            if art.relevance_score > unique[norm].relevance_score:
                unique[norm] = art
        else:
            unique[norm] = art

    # Сортировка: сначала по дате (самые свежие), потом по релевантности
    result = sorted(
        unique.values(),
        key=lambda a: (
            -(a.published.timestamp() if a.published else 0),
            -a.relevance_score,
        ),
    )

    # Ограничиваем количество
    result = result[: config.MAX_ARTICLES]

    # Обновляем seen
    for art in result:
        seen.add(_normalize_url(art.url))
    _save_seen_urls(seen)

    print(f"\n=== Найдено {len(result)} свежих статей (за {max_age_hours}ч) ===\n")
    return result
