# Epstein News Parser

Парсер свежих новостей о деле Джеффри Эпштейна для Telegram-канала.

## Источники

- **RSS-фиды**: BBC, NYT, Washington Post, Reuters, The Guardian, CNN, Fox News, NBC, ABC, Courthouse News, The Intercept, ProPublica, Daily Mail, NY Post
- **Google News RSS**: поиск по запросам "epstein files", "epstein documents unsealed"
- **CourtListener**: судебные документы и решения

## Установка

```bash
pip install -r requirements.txt
```

## Использование

### Сбор новостей (CLI)

```bash
# Дайджест + полный пост (по умолчанию)
python main.py

# Только короткий дайджест (топ-5)
python main.py --digest

# Полный пост со всеми статьями
python main.py --full

# Отдельные посты для каждой новости
python main.py --individual

# Простой текст
python main.py --plain

# JSON-вывод
python main.py --json

# Указать имя канала для подвала поста
python main.py --channel @your_channel

# Сохранить результат в файлы
python main.py --save

# Не пропускать ранее найденные статьи
python main.py --all-new
```

### Автоотправка в Telegram

```bash
# Настройка
export TG_BOT_TOKEN="123456:ABC-DEF..."
export TG_CHAT_ID="@your_channel"

# Отправить дайджест
python tg_bot.py

# Отправить полный пост
python tg_bot.py --full

# Отправить каждую новость отдельным постом
python tg_bot.py --individual

# Превью без отправки
python tg_bot.py --dry-run
```

### Автоматизация (cron)

```bash
# Каждые 6 часов
0 */6 * * * cd /path/to/epstein && python tg_bot.py >> cron.log 2>&1
```

## Структура

| Файл | Описание |
|------|----------|
| `main.py` | CLI-интерфейс |
| `parser.py` | Сбор новостей из всех источников |
| `formatter.py` | Форматирование постов (HTML/text) |
| `tg_bot.py` | Отправка в Telegram через Bot API |
| `config.py` | Настройки: ключевые слова, источники, лимиты |

## Настройка

Все параметры в `config.py`:

- `KEYWORDS` — ключевые слова для фильтрации
- `RSS_FEEDS` — список RSS-фидов
- `SCRAPE_SOURCES` — дополнительные источники
- `MIN_KEYWORD_MATCHES` — минимальное совпадение ключевых слов
- `MAX_ARTICLES` — максимум статей в подборке
