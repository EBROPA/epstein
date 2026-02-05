"""
Перевод заголовков статей на русский язык через Google Translate.
"""

import time

from deep_translator import GoogleTranslator


def translate_titles(titles: list[str], source: str = "en", target: str = "ru") -> list[str]:
    """Переводим список заголовков на русский. Батчами для скорости."""
    if not titles:
        return []

    translator = GoogleTranslator(source=source, target=target)
    translated = []

    # Google Translate принимает до ~5000 символов за раз
    # Переводим батчами по 10 заголовков
    batch_size = 10
    for i in range(0, len(titles), batch_size):
        batch = titles[i:i + batch_size]
        # Склеиваем через разделитель, который не встречается в заголовках
        separator = " ||| "
        combined = separator.join(batch)

        try:
            result = translator.translate(combined)
            parts = result.split("|||")
            # Если кол-во частей совпадает — разделяем
            if len(parts) == len(batch):
                translated.extend([p.strip() for p in parts])
            else:
                # Fallback: переводим по одному
                for title in batch:
                    try:
                        t = translator.translate(title)
                        translated.append(t.strip() if t else title)
                    except Exception:
                        translated.append(title)
        except Exception as exc:
            print(f"  [!] Ошибка перевода батча: {exc}")
            # Пробуем по одному
            for title in batch:
                try:
                    t = translator.translate(title)
                    translated.append(t.strip() if t else title)
                except Exception:
                    translated.append(title)

        time.sleep(0.3)  # Пауза между батчами

    return translated
