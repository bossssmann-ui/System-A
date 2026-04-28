"""
Конфигурация парсера тендеров.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Параметры Playwright
HEADLESS = True
TIMEOUT_MS = 30000  # 30 сек на загрузку страницы
RETRY_ATTEMPTS = 3
RETRY_DELAY_SEC = 2

# Параметры парсинга
DEFAULT_LIMIT = 50
MIN_NMC_RUB = 60000

# User-Agent (нормальный Chrome)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# URLs
ZAKUPKI_BASE_URL = "https://www.zakupki.gov.ru"
ZAKUPKI_SEARCH_URL = (
    "https://www.zakupki.gov.ru/epz/order/extendedsearch/results.html"
)

# Ключевые слова для поиска (в заголовке или описании)
SEARCH_KEYWORDS = [
    "грузоперев",
    "перевозка груз",
    "транспортн",
    "экспедир",
    "доставк",
    "логистическ",
]

# Стоп-фильтр: если в title есть эти слова — исключаем
STOP_KEYWORDS = [
    "авиа",
    "авиадоставк",
    "воздушн перевоз",
]

# База данных
DB_PATH = "tenders.db"
