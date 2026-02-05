#!/usr/bin/env python3
"""
Epstein News Parser — сбор свежих новостей о деле Эпштейна для Telegram-канала.

Использование:
    python main.py                  # Markdown-отчёт (по умолчанию) → report.md
    python main.py --digest         # Короткий дайджест .md (топ-5)
    python main.py --full           # Полный HTML-пост для Telegram
    python main.py --individual     # Отдельные HTML-посты
    python main.py --plain          # Простой текст
    python main.py --json           # JSON-вывод
    python main.py --hours 12       # Только за последние 12 часов
    python main.py --all-new        # Не пропускать ранее найденные
    python main.py --channel @name  # Указать имя канала
"""

import argparse
import json
import sys
from pathlib import Path

from parser import collect_all
from formatter import (
    format_telegram_html,
    format_digest_html,
    format_plain_text,
    format_individual_posts_html,
    format_markdown_report,
    format_digest_markdown,
)
import config


def main():
    ap = argparse.ArgumentParser(
        description="Парсер свежих новостей о деле Эпштейна для Telegram-канала"
    )
    ap.add_argument("--full", action="store_true", help="Полный HTML-пост")
    ap.add_argument("--digest", action="store_true", help="Короткий дайджест (топ-5)")
    ap.add_argument("--individual", action="store_true", help="Отдельные HTML-посты")
    ap.add_argument("--plain", action="store_true", help="Простой текст")
    ap.add_argument("--json", action="store_true", help="JSON-вывод")
    ap.add_argument("--all-new", action="store_true", help="Игнорировать кэш seen_urls")
    ap.add_argument("--hours", type=int, default=config.MAX_AGE_HOURS,
                     help=f"Максимальный возраст статей в часах (по умолчанию {config.MAX_AGE_HOURS})")
    ap.add_argument("--channel", type=str, default="", help="Имя TG-канала (напр. @epstein_news)")
    args = ap.parse_args()

    # Если ни один формат не выбран — по умолчанию Markdown-отчёт
    explicit_format = any([args.full, args.digest, args.individual, args.plain, args.json])

    # Сбор новостей (с фильтром по свежести)
    articles = collect_all(skip_seen=not args.all_new, max_age_hours=args.hours)

    if not articles:
        print(f"\nНовых статей за последние {args.hours}ч не найдено.")
        print("Попробуйте --hours 48 или --all-new")
        # Создаём пустой отчёт
        if not explicit_format:
            md = format_markdown_report([], channel_name=args.channel)
            Path(config.OUTPUT_MD_FILE).write_text(md, encoding="utf-8")
            print(f"\n[Пустой отчёт сохранён в {config.OUTPUT_MD_FILE}]")
        return

    # --- Markdown-отчёт (по умолчанию, всегда сохраняется) ---
    if not explicit_format:
        md = format_markdown_report(articles, channel_name=args.channel)
        Path(config.OUTPUT_MD_FILE).write_text(md, encoding="utf-8")
        print(f"[Отчёт сохранён в {config.OUTPUT_MD_FILE}]")
        print("\n" + md)
        return

    # JSON
    if args.json:
        data = [a.to_dict() for a in articles]
        output = json.dumps(data, ensure_ascii=False, indent=2)
        print(output)
        Path("output.json").write_text(output, encoding="utf-8")
        return

    # Дайджест (.md)
    if args.digest:
        md = format_digest_markdown(articles, channel_name=args.channel)
        Path(config.OUTPUT_MD_FILE).write_text(md, encoding="utf-8")
        print(f"[Дайджест сохранён в {config.OUTPUT_MD_FILE}]")
        print("\n" + md)

    # Полный HTML-пост
    if args.full:
        post = format_telegram_html(articles, channel_name=args.channel)
        print("\n" + "=" * 50)
        print("ПОЛНЫЙ ПОСТ (HTML для Telegram):")
        print("=" * 50)
        print(post)
        Path(config.OUTPUT_HTML_FILE).write_text(post, encoding="utf-8")
        print(f"\n[Сохранено в {config.OUTPUT_HTML_FILE}]")

    # Отдельные посты
    if args.individual:
        posts = format_individual_posts_html(articles)
        print("\n" + "=" * 50)
        print(f"ОТДЕЛЬНЫЕ ПОСТЫ ({len(posts)} шт.):")
        print("=" * 50)
        for i, p in enumerate(posts, 1):
            print(f"\n--- Пост #{i} ---")
            print(p)

    # Plain text
    if args.plain:
        text = format_plain_text(articles)
        print("\n" + text)
        Path(config.OUTPUT_FILE).write_text(text, encoding="utf-8")
        print(f"\n[Сохранено в {config.OUTPUT_FILE}]")

    # Всегда сохраняем .md отчёт дополнительно
    md = format_markdown_report(articles, channel_name=args.channel)
    Path(config.OUTPUT_MD_FILE).write_text(md, encoding="utf-8")
    print(f"\n[MD-отчёт сохранён в {config.OUTPUT_MD_FILE}]")


if __name__ == "__main__":
    main()
