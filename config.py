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
    "epstein island",
    "epstein associate",
    "epstein client",
    "epstein accuser",
    "epstein trafficking",
    "epstein plea",
    "epstein settlement",
    "epstein flight log",
    "lolita express",
    "jean-luc brunel",
    "les wexner",
    "prince andrew",
    "virginia giuffre",
]

# Минимальное кол-во совпадений ключевых слов для включения статьи
MIN_KEYWORD_MATCHES = 1

# RSS-фиды новостных источников
RSS_FEEDS = [
    # === Топ-СМИ (широкий охват) ===
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.washingtonpost.com/rss/national",
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.theguardian.com/theguardian/us-news/rss",
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.foxnews.com/foxnews/latest",
    "https://feeds.nbcnews.com/nbcnews/public/news",
    "https://feeds.abcnews.com/abcnews/topstories",
    "https://feeds.cbsnews.com/CBSNewsMain",
    "https://feeds.skynews.com/feeds/rss/us.xml",
    # === Таблоиды / вирусный контент / максимальный охват ===
    "https://www.dailymail.co.uk/articles.rss",
    "https://nypost.com/feed/",
    "https://www.thesun.co.uk/feed/",
    "https://www.mirror.co.uk/news/rss.xml",
    "https://pagesix.com/feed/",
    "https://www.tmz.com/rss.xml",
    "https://www.thedailybeast.com/rss",
    "https://www.insider.com/rss",
    "https://www.buzzfeednews.com/rss",
    # === Расследования / аналитика ===
    "https://theintercept.com/feed/?rss",
    "https://www.propublica.org/feeds/propublica/main",
    "https://www.rollingstone.com/feed/",
    "https://www.vanityfair.com/feed/rss",
    "https://www.newyorker.com/feed/news",
    # === Юридические / судебные ===
    "https://www.courthousenews.com/feed/",
    "https://www.law.com/rss/",
    "https://www.lawfaremedia.org/feed",
    "https://abovethelaw.com/feed/",
    # === Политика (часто пересекается с делом) ===
    "https://www.politico.com/rss/politicopicks.xml",
    "https://thehill.com/feed/",
    "https://www.rawstory.com/feed/",
    "https://www.salon.com/feed/",
    # === Агрегаторы ===
    "https://news.yahoo.com/rss",
    "https://feeds.feedburner.com/ndaborq",
]

# Прямые источники для скрейпинга (HTML / RSS-поиск)
SCRAPE_SOURCES = [
    {
        "name": "CourtListener (Epstein)",
        "url": "https://www.courtlistener.com/?q=epstein&type=r&order_by=score+desc",
        "type": "courtlistener",
    },
    # Google News RSS — свежие за 1 день
    {
        "name": "Google News — Epstein files",
        "url": "https://news.google.com/rss/search?q=epstein+files+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein documents",
        "url": "https://news.google.com/rss/search?q=epstein+documents+unsealed+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein latest",
        "url": "https://news.google.com/rss/search?q=jeffrey+epstein+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein list names",
        "url": "https://news.google.com/rss/search?q=epstein+list+names+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Ghislaine Maxwell",
        "url": "https://news.google.com/rss/search?q=ghislaine+maxwell+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein island",
        "url": "https://news.google.com/rss/search?q=epstein+island+flight+log+when:1d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news_rss",
    },
    {
        "name": "Google News — Epstein trafficking",
        "url": "https://news.google.com/rss/search?q=epstein+trafficking+victim+when:1d&hl=en-US&gl=US&ceid=US:en",
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

# Максимальный возраст статьи в часах (по умолчанию 24ч — только за последние сутки)
MAX_AGE_HOURS = 24

# Максимальное кол-во статей в итоговой подборке
MAX_ARTICLES = 30

# Файл для хранения уже обработанных ссылок (дедупликация)
SEEN_URLS_FILE = "seen_urls.json"

# Файлы с результатами
OUTPUT_FILE = "output_post.txt"
OUTPUT_HTML_FILE = "output_post.html"
OUTPUT_MD_FILE = "report.md"
