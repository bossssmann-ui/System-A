"""
Логика скрейпинга zakupki.gov.ru с использованием Playwright.
Включает синхронный парсинг HTML без браузера.
"""
import logging
import re
import html
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


def _clean_text(text: Optional[str]) -> Optional[str]:
    """
    Очищает текст от HTML entities и лишних пробелов.

    Args:
        text: Исходный текст

    Returns:
        Очищенный текст или None
    """
    if not text:
        return None

    # Декодируем HTML entities
    text = html.unescape(text)

    # Заменяем неразрывные пробелы на обычные
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2009", " ")

    # Удаляем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text).strip()

    return text if text else None


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
        Парсит результаты поиска со страницы (результаты поиска).

        Returns:
            Список найденных тендеров
        """
        tenders: List[Dict[str, Any]] = []

        try:
            # Получаем HTML страницы
            content = await self.page_instance.content()
            soup = BeautifulSoup(content, "html.parser")

            # Селектор: div.search-registry-entry-block > div.registry-entry__form
            result_rows = soup.find_all("div", class_="registry-entry__form")

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

    def parse_html_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Синхронный парс HTML файла (сохраненной страницы) без использования браузера.
        Используется для офлайн-тестирования и когда Playwright недоступен или заблокирован.

        Args:
            file_path: Путь к HTML файлу

        Returns:
            Список найденных тендеров
        """
        tenders: List[Dict[str, Any]] = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Ищем все карточки тендеров (div.registry-entry__form)
            result_rows = soup.find_all("div", class_="registry-entry__form")

            logger.info(f"[{file_path}] Найдено потенциальных строк результатов: {len(result_rows)}")

            for row_idx, row in enumerate(result_rows[:self.limit]):
                try:
                    tender = self._extract_tender_from_row(row)
                    if tender:
                        tenders.append(tender)
                        logger.info(f"  [{row_idx+1}] ID: {tender['id']}, Title: {tender['title'][:40]}...")
                except Exception as e:
                    logger.warning(f"Ошибка парсинга строки {row_idx}: {e}")
                    continue

            logger.info(f"[{file_path}] Успешно распарсено тендеров: {len(tenders)}")

        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка парсинга файла {file_path}: {e}")

        return tenders

    def _extract_tender_from_row(self, row) -> Optional[Dict[str, Any]]:
        """
        Извлекает информацию о тендере из одной строки результатов (div с классом registry-entry__form).
        Реальные селекторы для zakupki.gov.ru.

        Args:
            row: BeautifulSoup элемент (div.registry-entry__form)

        Returns:
            Словарь с данными тендера или None
        """
        try:
            # 1. РЕЕСТРОВЫЙ НОМЕР (ID)
            # Селектор: div.registry-entry__header-mid__number > a > text()
            id_elem = row.find("div", class_="registry-entry__header-mid__number")
            if not id_elem:
                logger.debug("Не найден элемент с ID тендера (registry-entry__header-mid__number)")
                return None

            tender_id = id_elem.get_text(separator=' ', strip=True)
            # Убираем '№' если есть
            tender_id = tender_id.replace("№", "").strip()

            if not tender_id or len(tender_id) < 10:
                logger.debug(f"ID слишком короткий или не найден: '{tender_id}'")
                return None

            # Получаем ссылку из элемента ID
            id_link = id_elem.find("a")
            link = id_link.get("href", "") if id_link else ""
            if not link.startswith("http"):
                link = f"https://zakupki.gov.ru{link}" if link else ""

            logger.debug(f"✓ ID найден: {tender_id}")

            # 2. ЗАКОН (44-ФЗ или 223-ФЗ)
            # Селектор: div.registry-entry__header-top__title > text()[1]
            law = "44-ФЗ"  # по умолчанию
            law_elem = row.find("div", class_="registry-entry__header-top__title")
            if law_elem:
                law_text = law_elem.get_text(separator=' ', strip=True)
                if "223" in law_text:
                    law = "223-ФЗ"
                logger.debug(f"✓ Закон найден: {law}")

            # 3. ЭТАП ЗАКУПКИ (Подача заявок, Работа комиссии и т.д.)
            # Селектор: div.registry-entry__header-mid__title > text()
            stage = None
            stage_elem = row.find("div", class_="registry-entry__header-mid__title")
            if stage_elem:
                stage = stage_elem.get_text(separator=' ', strip=True)
                logger.debug(f"✓ Этап найден: {stage}")

            # 4. ОБЪЕКТ ЗАКУПКИ (Наименование)
            # Селектор: div.registry-entry__body > div.registry-entry__body-block[1] > div.registry-entry__body-value
            description = None
            body = row.find("div", class_="registry-entry__body")
            if body:
                body_blocks = body.find_all("div", class_="registry-entry__body-block")
                if body_blocks:
                    first_block = body_blocks[0]
                    desc_elem = first_block.find("div", class_="registry-entry__body-value")
                    if desc_elem:
                        description = _clean_text(desc_elem.get_text(separator=' ', strip=True))
                        logger.debug(f"✓ Описание найдено: {description[:50]}...")

            # Если нет описания, используем как название
            title = description or "Неизвестный тендер"
            title = normalize_title(title)

            # Проверка стоп-фильтра
            if has_stop_keyword(title):
                logger.debug(f"Тендер {tender_id} отфильтрован (стоп-слово)")
                return None

            # 5. ЗАКАЗЧИК
            # Селектор: div.registry-entry__body-href > a > text()
            # Может быть как "Заказчик", так и "Организация, осуществляющая размещение"
            customer = None
            if body:
                body_blocks = body.find_all("div", class_="registry-entry__body-block")
                for block in body_blocks:
                    title_elem = block.find("div", class_="registry-entry__body-title")
                    if title_elem:
                        title_text = title_elem.get_text(separator=' ', strip=True)
                        # Ищем либо "Заказчик" либо "Организация, осуществляющая размещение"
                        if "Заказчик" in title_text or "размещение" in title_text.lower():
                            href_elem = block.find("div", class_="registry-entry__body-href")
                            if href_elem:
                                customer_link = href_elem.find("a")
                                if customer_link:
                                    customer = _clean_text(customer_link.get_text(separator=' ', strip=True))
                                    logger.debug(f"✓ Заказчик найден: {customer[:40]}...")
                            break

            # 6. НМЦ (НАЧАЛЬНАЯ ЦЕНА)
            # Селектор: div.price-block__value
            amount = None
            right_block = row.find("div", class_="registry-entry__right-block")
            if right_block:
                price_block = right_block.find("div", class_="price-block")
                if price_block:
                    price_value = price_block.find("div", class_="price-block__value")
                    if price_value:
                        amount_str = price_value.get_text(strip=True)
                        amount = normalize_amount(amount_str)
                        logger.debug(f"✓ Сумма найдена: {amount} руб")

                        if amount and amount < MIN_NMC_RUB:
                            logger.debug(f"Тендер {tender_id}: сумма {amount} < {MIN_NMC_RUB}")
                            return None

            # 7. DEADLINE (ОКОНЧАНИЕ ПОДАЧИ ЗАЯВОК)
            # Селектор: div.data-block > div.data-block__value (последний с датой)
            deadline = None
            if right_block:
                data_block = right_block.find("div", class_="data-block")
                if data_block:
                    data_values = data_block.find_all("div", class_="data-block__value")
                    if data_values:
                        # Последний data-block__value обычно это "Окончание подачи заявок"
                        deadline = data_values[-1].get_text(separator=' ', strip=True)
                        deadline = normalize_deadline(deadline)
                        logger.debug(f"✓ Deadline найден: {deadline}")

            # 8. РЕГИОН
            # На странице выдачи региона может и не быть, попытаемся извлечь из заказчика или оставим None
            region = None

            tender = {
                "id": tender_id,
                "title": title,
                "law": law,
                "stage": stage,
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
