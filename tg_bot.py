#!/usr/bin/env python3
"""
Опциональный модуль: автоматическая отправка постов в Telegram-канал через Bot API.

Использование:
    1. Создай бота через @BotFather, получи токен
    2. Добавь бота администратором в канал
    3. Установи переменные окружения:
        export TG_BOT_TOKEN="123456:ABC-DEF..."
        export TG_CHAT_ID="@your_channel"  # или числовой ID канала
    4. Запусти:
        python tg_bot.py                # Дайджест
        python tg_bot.py --full         # Полный пост
        python tg_bot.py --individual   # Отдельные посты
"""

import argparse
import os
import sys
import time

import requests

from parser import collect_all
from formatter import (
    format_telegram_html,
    format_digest_html,
    format_individual_posts_html,
)


def send_message(bot_token: str, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """Отправка сообщения через Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            print(f"  [OK] Сообщение отправлено")
            return True
        else:
            print(f"  [ERR] Telegram API: {data.get('description', 'unknown error')}")
            return False
    except requests.RequestException as exc:
        print(f"  [ERR] Ошибка отправки: {exc}")
        return False


def main():
    ap = argparse.ArgumentParser(description="Отправка новостей Эпштейна в Telegram")
    ap.add_argument("--full", action="store_true", help="Полный пост")
    ap.add_argument("--individual", action="store_true", help="Отдельные посты")
    ap.add_argument("--all-new", action="store_true", help="Не пропускать ранее найденные")
    ap.add_argument("--dry-run", action="store_true", help="Не отправлять, только показать")
    args = ap.parse_args()

    bot_token = os.environ.get("TG_BOT_TOKEN", "")
    chat_id = os.environ.get("TG_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("Ошибка: установите TG_BOT_TOKEN и TG_CHAT_ID")
        print("  export TG_BOT_TOKEN='123456:ABC-DEF...'")
        print("  export TG_CHAT_ID='@your_channel'")
        sys.exit(1)

    articles = collect_all(skip_seen=not args.all_new)
    if not articles:
        print("Новых статей не найдено.")
        return

    if args.individual:
        posts = format_individual_posts_html(articles)
        print(f"\nОтправка {len(posts)} отдельных постов...")
        for i, post in enumerate(posts, 1):
            print(f"\n--- Пост #{i} ---")
            if args.dry_run:
                print(post)
            else:
                send_message(bot_token, chat_id, post)
                time.sleep(1)  # Лимит Telegram: ~30 сообщений/сек
    elif args.full:
        post = format_telegram_html(articles, channel_name=chat_id)
        print("\nОтправка полного поста...")
        if args.dry_run:
            print(post)
        else:
            # Telegram лимит — 4096 символов на сообщение
            if len(post) > 4096:
                chunks = _split_message(post, 4096)
                for chunk in chunks:
                    send_message(bot_token, chat_id, chunk)
                    time.sleep(0.5)
            else:
                send_message(bot_token, chat_id, post)
    else:
        # По умолчанию — дайджест
        post = format_digest_html(articles, channel_name=chat_id)
        print("\nОтправка дайджеста...")
        if args.dry_run:
            print(post)
        else:
            send_message(bot_token, chat_id, post)

    print("\nГотово!")


def _split_message(text: str, max_len: int) -> list[str]:
    """Разбиваем длинное сообщение на части по пустым строкам."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_len:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current:
        chunks.append(current.strip())

    return chunks


if __name__ == "__main__":
    main()
