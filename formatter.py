"""
Форматирование собранных новостей в пост для Telegram-канала.
Поддержка: plain text, HTML (Telegram Bot API), Markdown.
"""

from datetime import datetime, timezone
from parser import Article


# ---------------------------------------------------------------------------
# Telegram HTML (для Bot API — parse_mode=HTML)
# ---------------------------------------------------------------------------

def format_telegram_html(articles: list[Article], channel_name: str = "") -> str:
    """Генерирует готовый HTML-пост для Telegram."""
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    lines = []

    lines.append(f"<b>📋 Дело Эпштейна — свежие новости</b>")
    lines.append(f"<i>{now}</i>")
    lines.append("")

    if not articles:
        lines.append("Новых публикаций не найдено. Следим дальше.")
        return "\n".join(lines)

    for i, art in enumerate(articles, 1):
        # Заголовок со ссылкой
        title_escaped = _escape_html(art.title)
        lines.append(f"<b>{i}.</b> <a href=\"{art.url}\">{title_escaped}</a>")

        # Источник и дата
        meta_parts = [f"📰 {_escape_html(art.source)}"]
        if art.published:
            meta_parts.append(f"🕐 {art.published.strftime('%d.%m.%Y %H:%M')}")
        lines.append(f"<i>{' | '.join(meta_parts)}</i>")

        # Краткое содержание
        if art.summary:
            short = _truncate(art.summary, 200)
            lines.append(f"{_escape_html(short)}")

        lines.append("")  # пустая строка между статьями

    # Подвал
    lines.append("—")
    if channel_name:
        lines.append(f"Подписывайтесь: {channel_name}")
    lines.append(f"#Эпштейн #EpsteinFiles #Новости")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Краткий дайджест (1 пост — топ-5)
# ---------------------------------------------------------------------------

def format_digest_html(articles: list[Article], channel_name: str = "") -> str:
    """Короткий дайджест — топ-5 новостей для одного поста."""
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    top = articles[:5]
    lines = []

    lines.append(f"<b>🔥 Эпштейн: дайджест дня — {now}</b>")
    lines.append("")

    for i, art in enumerate(top, 1):
        title_escaped = _escape_html(art.title)
        source_escaped = _escape_html(art.source)
        lines.append(f"{i}. <a href=\"{art.url}\">{title_escaped}</a> ({source_escaped})")

    lines.append("")
    lines.append(f"Всего найдено статей: {len(articles)}")
    lines.append("")
    if channel_name:
        lines.append(f"Подписывайтесь: {channel_name}")
    lines.append("#Эпштейн #EpsteinFiles")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plain text (для копирования вручную)
# ---------------------------------------------------------------------------

def format_plain_text(articles: list[Article]) -> str:
    """Простой текстовый формат."""
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    lines = []

    lines.append(f"ДЕЛО ЭПШТЕЙНА — СВЕЖИЕ НОВОСТИ ({now})")
    lines.append("=" * 50)
    lines.append("")

    for i, art in enumerate(articles, 1):
        lines.append(f"{i}. {art.title}")
        lines.append(f"   Источник: {art.source}")
        if art.published:
            lines.append(f"   Дата: {art.published.strftime('%d.%m.%Y %H:%M')}")
        lines.append(f"   Ссылка: {art.url}")
        if art.summary:
            short = _truncate(art.summary, 250)
            lines.append(f"   {short}")
        lines.append(f"   Релевантность: {art.relevance_score} (слова: {', '.join(art.keywords_found)})")
        lines.append("")

    lines.append(f"Итого: {len(articles)} статей")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Отдельные посты (каждая статья — отдельный пост)
# ---------------------------------------------------------------------------

def format_individual_posts_html(articles: list[Article]) -> list[str]:
    """Каждая статья — отдельный HTML-пост для Telegram."""
    posts = []
    for art in articles:
        title_escaped = _escape_html(art.title)
        lines = []
        lines.append(f"<b>📰 {title_escaped}</b>")
        lines.append("")

        if art.summary:
            lines.append(_escape_html(_truncate(art.summary, 300)))
            lines.append("")

        meta = [f"Источник: {_escape_html(art.source)}"]
        if art.published:
            meta.append(f"Дата: {art.published.strftime('%d.%m.%Y %H:%M')}")
        lines.append("<i>" + " | ".join(meta) + "</i>")
        lines.append("")
        lines.append(f"<a href=\"{art.url}\">Читать полностью →</a>")
        lines.append("")
        lines.append("#Эпштейн #EpsteinFiles")

        posts.append("\n".join(lines))
    return posts


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def _escape_html(text: str) -> str:
    """Экранирование для Telegram HTML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "..."
