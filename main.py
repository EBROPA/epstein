#!/usr/bin/env python3
"""
Epstein News Parser — сбор свежих новостей о деле Эпштейна для Telegram-канала.

Использование:
    python main.py                  # Полный сбор + вывод дайджеста
    python main.py --full           # Полный пост со всеми статьями
    python main.py --digest         # Короткий дайджест (топ-5)
    python main.py --individual     # Отдельные посты для каждой новости
    python main.py --plain          # Простой текст
    python main.py --all-new        # Не пропускать ранее найденные
    python main.py --channel @name  # Указать имя канала для подвала
    python main.py --json           # Вывести сырые данные в JSON
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
)
import config


def main():
    ap = argparse.ArgumentParser(
        description="Парсер новостей о деле Эпштейна для Telegram-канала"
    )
    ap.add_argument("--full", action="store_true", help="Полный HTML-пост")
    ap.add_argument("--digest", action="store_true", help="Короткий дайджест (топ-5)")
    ap.add_argument("--individual", action="store_true", help="Отдельные посты")
    ap.add_argument("--plain", action="store_true", help="Простой текст")
    ap.add_argument("--json", action="store_true", help="JSON-вывод")
    ap.add_argument("--all-new", action="store_true", help="Игнорировать кэш seen_urls")
    ap.add_argument("--channel", type=str, default="", help="Имя TG-канала (напр. @epstein_news)")
    ap.add_argument("--save", action="store_true", help="Сохранить результат в файлы")
    args = ap.parse_args()

    # Если ни один формат не выбран — по умолчанию дайджест + full
    if not any([args.full, args.digest, args.individual, args.plain, args.json]):
        args.digest = True
        args.full = True

    # Сбор новостей
    articles = collect_all(skip_seen=not args.all_new)

    if not articles:
        print("\nНовых статей не найдено. Попробуйте --all-new или подождите обновлений.")
        return

    # JSON
    if args.json:
        data = [a.to_dict() for a in articles]
        output = json.dumps(data, ensure_ascii=False, indent=2)
        print(output)
        if args.save:
            Path("output.json").write_text(output, encoding="utf-8")
            print("\n[Сохранено в output.json]")
        return

    # Дайджест
    if args.digest:
        post = format_digest_html(articles, channel_name=args.channel)
        print("\n" + "=" * 50)
        print("ДАЙДЖЕСТ (HTML для Telegram):")
        print("=" * 50)
        print(post)
        if args.save:
            Path("output_digest.html").write_text(post, encoding="utf-8")
            print("\n[Сохранено в output_digest.html]")

    # Полный пост
    if args.full:
        post = format_telegram_html(articles, channel_name=args.channel)
        print("\n" + "=" * 50)
        print("ПОЛНЫЙ ПОСТ (HTML для Telegram):")
        print("=" * 50)
        print(post)
        if args.save:
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
        print("\n" + "=" * 50)
        print("PLAIN TEXT:")
        print("=" * 50)
        print(text)
        if args.save:
            Path(config.OUTPUT_FILE).write_text(text, encoding="utf-8")
            print(f"\n[Сохранено в {config.OUTPUT_FILE}]")


if __name__ == "__main__":
    main()
