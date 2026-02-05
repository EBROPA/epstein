"""
Конфигурация парсера новостей Эпштейна.
"""

# Ключевые слова для поиска (английские — основные источники англоязычные)
KEYWORDS = [
    "epstein",
    "ghislaine maxwell",
    "epstein files",
    "epstein documents",
    "epstein list",
    "epstein unsealed",
    "epstein court",
    "epstein deposition",
    "epstein victim",
    "jeffrey epstein",
]

# Минимальное кол-во совпадений ключевых слов для включения статьи
MIN_KEYWORD_MATCHES = 1

# RSS-фиды новостных источников
RSS_FEEDS = [
    # Крупные англоязычные СМИ
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.washingtonpost.com/rss/national",
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.theguardian.com/theguardian/us-news/rss",
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.foxnews.com/foxnews/latest",
    "https://feeds.nbcnews.com/nbcnews/public/news",
    "https://feeds.abcnews.com/abcnews/topstories",
    # Юридические / судебные
    "https://www.courthousenews.com/feed/",
    "https://www.law.com/rss/",
    # Расследовательская журналистика
    "https://theintercept.com/feed/?rss",
    "https://www.propublica.org/feeds/propublica/main",
    "https://www.vice.com/en/rss",
    # Daily Mail — часто первыми публикуют подробности
    "https://www.dailymail.co.uk/articles.rss",
    # New York Post
    "https://nypost.com/feed/",
]

# Прямые источники для скрейпинга (HTML)
SCRAPE_SOURCES = [
    {
        "name": "CourtListener (Epstein)",
        "url": "https://www.courtlistener.com/?q=epstein&type=r&order_by=score+desc",
        "type": "courtlistener",
    },
    {
        "name": "Google News — Epstein",
        "url": "https://news.google.com/rss/search?q=epstein+files&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein documents",
        "url": "https://news.google.com/rss/search?q=epstein+documents+unsealed&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
]

# Заголовки для HTTP-запросов
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Таймаут запросов (секунды)
REQUEST_TIMEOUT = 15

# Максимальное кол-во статей в итоговой подборке
MAX_ARTICLES = 20

# Файл для хранения уже обработанных ссылок (дедупликация)
SEEN_URLS_FILE = "seen_urls.json"

# Файл с результатами
OUTPUT_FILE = "output_post.txt"
OUTPUT_HTML_FILE = "output_post.html"
