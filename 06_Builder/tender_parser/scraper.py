"""
Логика скрейпинга zakupki.gov.ru с использованием Playwright.
"""
import logging
import time
from typing import List, Dict, Any, Optional

try:
    from playwright.async_api import async_playwright, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

import asyncio

from config import (
    HEADLESS,
    USER_AGENT,
    TIMEOUT_MS,
    RETRY_ATTEMPTS,
    RETRY_DELAY_SEC,
    ZAKUPKI_SEARCH_URL,
    SEARCH_KEYWORDS,
    MIN_NMC_RUB,
)
from filters import (
    has_stop_keyword,
    normalize_amount,
    normalize_deadline,
    normalize_title,
)

logger = logging.getLogger(__name__)


class ZakupkiScraper:
    """Скрейпер для zakupki.gov.ru."""

    def __init__(self, headless: bool = HEADLESS, limit: int = 50):
        """
        Args:
            headless: Запускать ли Playwright в headless режиме
            limit: Сколько тендеров парсить
        """
        self.headless = headless
        self.limit = limit
        self.browser_instance = None
        self.context_instance = None
        self.page_instance: Optional[Page] = None

    async def _launch_browser(self):
        """Запускает браузер Chromium."""
        playwright = await async_playwright().start()
        self.browser_instance = await playwright.chromium.launch(
            headless=self.headless
        )
        self.context_instance = await self.browser_instance.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
        )
        self.page_instance = await self.context_instance.new_page()
        logger.info("Браузер запущен")

    async def _close_browser(self):
        """Закрывает браузер."""
        if self.page_instance:
            await self.page_instance.close()
        if self.context_instance:
            await self.context_instance.close()
        if self.browser_instance:
            await self.browser_instance.close()
        logger.info("Браузер закрыт")

    async def _navigate_with_retry(self, url: str) -> bool:
        """
        Навигирует на URL с retry логикой.

        Args:
            url: URL для перехода

        Returns:
            True если успешно, False иначе
        """
        for attempt in range(RETRY_ATTEMPTS):
            try:
                await self.page_instance.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
                logger.info(f"Успешно загружена страница {url}")
                return True
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    delay = RETRY_DELAY_SEC * (2 ** attempt)
                    logger.warning(
                        f"Ошибка загрузки (попытка {attempt + 1}/{RETRY_ATTEMPTS}): {e}. "
                        f"Ожидание {delay}с..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Не удалось загрузить {url} после {RETRY_ATTEMPTS} попыток")
                    return False

        return False

    async def _apply_filters(self) -> bool:
        """
        Применяет фильтры на странице поиска.
        Это сложный процесс, зависит от структуры HTML zakupki.gov.ru.

        Returns:
            True если фильтры применены, False иначе
        """
        try:
            # Примечание: структура закупки.gov.ru часто меняется.
            # Здесь используются примерные селекторы. Может потребоваться отладка.

            # Ждём загрузки страницы поиска
            await self.page_instance.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)

            # Попытка установить фильтры через форму или API
            # (в реальном коде потребуется анализ структуры сайта)
            logger.info("Попытка применения фильтров...")

            # Для MVP: если страница загружена, ищем элементы фильтров
            # Временно логируем содержимое страницы для отладки
            content = await self.page_instance.content()
            if "результаты" in content.lower() or "закупки" in content.lower():
                logger.info("Страница загружена, содержит поисковый контент")
                return True
            else:
                logger.warning("Неожиданная структура страницы")
                return False

        except Exception as e:
            logger.error(f"Ошибка при применении фильтров: {e}")
            return False

    async def _parse_results(self) -> List[Dict[str, Any]]:
        """
        Парсит результаты поиска со страницы.

        Returns:
            Список найденных тендеров
        """
        tenders: List[Dict[str, Any]] = []

        try:
            # Получаем HTML страницы
            content = await self.page_instance.content()
            soup = BeautifulSoup(content, "html.parser")

            # Примечание: селекторы зависят от структуры закупки.gov.ru
            # Здесь используются примерные селекторы, требуется уточнение

            # Ищем таблицу результатов или список тендеров
            # Типичная структура: <tr> с классом, содержащим информацию о тендере
            result_rows = soup.find_all("tr", class_=lambda x: x and "register" in (x or "").lower())

            if not result_rows:
                # Альтернативный поиск
                result_rows = soup.find_all("div", class_=lambda x: x and "search-result" in (x or "").lower())

            logger.info(f"Найдено потенциальных строк результатов: {len(result_rows)}")

            for row_idx, row in enumerate(result_rows[:self.limit]):
                try:
                    tender = self._extract_tender_from_row(row)
                    if tender:
                        tenders.append(tender)
                except Exception as e:
                    logger.warning(f"Ошибка парсинга строки {row_idx}: {e}")
                    continue

            logger.info(f"Успешно распарсено тендеров: {len(tenders)}")

        except Exception as e:
            logger.error(f"Ошибка парсинга результатов: {e}")

        return tenders

    def _extract_tender_from_row(self, row) -> Optional[Dict[str, Any]]:
        """
        Извлекает информацию о тендере из одной строки результатов.

        Args:
            row: BeautifulSoup элемент строки

        Returns:
            Словарь с данными тендера или None
        """
        try:
            # Примечание: требуется анализ HTML структуры закупки.gov.ru
            # Здесь используются примерные селекторы

            # Попытка найти ID (реестровый номер)
            id_elem = row.find("a", href=lambda x: x and "/order/" in x)
            if not id_elem:
                return None

            tender_id = id_elem.text.strip()
            link = id_elem.get("href", "")
            if not link.startswith("http"):
                link = f"https://www.zakupki.gov.ru{link}"

            # Заголовок
            title_elem = row.find("span", class_=lambda x: x and "title" in (x or "").lower())
            title = title_elem.text.strip() if title_elem else "Неизвестно"
            title = normalize_title(title)

            # Проверка стоп-фильтра
            if has_stop_keyword(title):
                logger.debug(f"Тендер {tender_id} отфильтрован (стоп-слово)")
                return None

            # Попытка найти другие поля
            cells = row.find_all("td") if hasattr(row, "find_all") else [row]

            # НМЦ (сумма)
            amount_elem = None
            for cell in cells:
                if "руб" in cell.text.lower() or any(c.isdigit() for c in cell.text):
                    amount_elem = cell
                    break

            amount = None
            if amount_elem:
                amount = normalize_amount(amount_elem.text)
                if amount and amount < MIN_NMC_RUB:
                    logger.debug(f"Тендер {tender_id}: сумма {amount} < {MIN_NMC_RUB}")
                    return None

            # Регион, заказчик, deadline — требуют дополнительного анализа структуры
            region = "Россия"  # По умолчанию
            customer = "Неизвестно"
            deadline = None
            law = "44-ФЗ"  # По умолчанию
            description = None

            tender = {
                "id": tender_id,
                "title": title,
                "law": law,
                "customer": customer,
                "amount": amount,
                "region": region,
                "deadline": deadline,
                "link": link,
                "description": description,
            }

            return tender

        except Exception as e:
            logger.error(f"Ошибка при извлечении данных из строки: {e}")
            return None

    async def run(self) -> List[Dict[str, Any]]:
        """
        Основной метод: запускает парсинг и возвращает список тендеров.

        Returns:
            Список найденных тендеров
        """
        tenders = []

        try:
            await self._launch_browser()

            # Навигируемся на страницу поиска
            if not await self._navigate_with_retry(ZAKUPKI_SEARCH_URL):
                logger.error("Не удалось загрузить страницу поиска")
                return tenders

            # Применяем фильтры
            if not await self._apply_filters():
                logger.warning("Фильтры не применены полностью, продолжаем")

            # Парсим результаты
            tenders = await self._parse_results()

        except Exception as e:
            logger.error(f"Ошибка при парсинге: {e}")
        finally:
            await self._close_browser()

        return tenders


def get_mock_tenders() -> List[Dict[str, Any]]:
    """
    Возвращает тестовые данные если Playwright не установлен.
    Используется для отладки и тестирования в окружении без браузера.

    Returns:
        Список тестовых тендеров
    """
    return [
        {
            "id": "0132300156625000001",
            "title": "Оказание услуг по грузоперевозкам и доставке грузов на Дальнем Востоке",
            "law": "44-ФЗ",
            "customer": "Администрация Приморского края",
            "amount": 2500000,
            "region": "Приморский край",
            "deadline": "2026-05-15 18:00:00",
            "link": "https://www.zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0132300156625000001",
            "description": "Оказание услуг по доставке грузов и материалов",
        },
        {
            "id": "0323100087626000003",
            "title": "Услуги по перевозке оборудования и логистическому сопровождению",
            "law": "223-ФЗ",
            "customer": "ООО Примтеплоэнергосбыт",
            "amount": 850000,
            "region": "Приморский край",
            "deadline": "2026-05-10 17:00:00",
            "link": "https://www.zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0323100087626000003",
            "description": "Транспортное обеспечение логистических операций",
        },
        {
            "id": "0432150012345000005",
            "title": "Экспедиторское обслуживание и доставка контейнеризованных грузов",
            "law": "44-ФЗ",
            "customer": "Портовая компания 'Тихий Океан'",
            "amount": 1750000,
            "region": "Приморский край",
            "deadline": "2026-05-20 10:00:00",
            "link": "https://www.zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0432150012345000005",
            "description": "Услуги по экспедированию и доставке",
        },
    ]


def run_scraper(headless: bool = HEADLESS, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Вспомогательная функция для запуска скрейпера из синхронного кода.

    Args:
        headless: Режим headless
        limit: Лимит тендеров

    Returns:
        Список тендеров
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright не установлен, используются тестовые данные")
        return get_mock_tenders()[:limit]

    scraper = ZakupkiScraper(headless=headless, limit=limit)
    return asyncio.run(scraper.run())
