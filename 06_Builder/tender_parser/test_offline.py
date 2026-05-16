#!/usr/bin/env python3
"""
Тестовый скрипт для офлайн-парсинга HTML файлов zakupki.gov.ru.
Не требует браузера, сети и Playwright.
Загружает результаты в SQLite базу.
"""
import logging
import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Импорт из проекта
from scraper import ZakupkiScraper
from storage import TenderDatabase

def print_tender(tender: Dict[str, Any], index: int = 0):
    """Красивый вывод одного тендера."""
    print(f"\n{'='*80}")
    print(f"Тендер #{index}")
    print(f"{'='*80}")
    print(f"ID:           {tender.get('id', 'N/A')}")
    print(f"Название:     {tender.get('title', 'N/A')}")
    print(f"Закон:        {tender.get('law', 'N/A')}")
    print(f"Этап:         {tender.get('stage', 'N/A')}")
    print(f"Заказчик:     {tender.get('customer', 'N/A')}")
    print(f"Сумма:        {tender.get('amount', 'N/A')} руб.")
    print(f"Регион:       {tender.get('region', 'N/A')}")
    print(f"Deadline:     {tender.get('deadline', 'N/A')}")
    print(f"Регион (получ из описания): {tender.get('region', 'N/A')}")
    if tender.get('description'):
        desc = tender['description'][:60] + "..." if len(tender['description']) > 60 else tender['description']
        print(f"Описание:     {desc}")
    if tender.get('link'):
        print(f"Ссылка:       {tender['link']}")

def main():
    """Основная функция теста."""
    logger.info("=" * 80)
    logger.info("ТЕСТ ОФЛАЙН ПАРСИНГА HTML ZAKUPKI.GOV.RU")
    logger.info("=" * 80)

    # Пути к HTML файлам
    base_dir = Path(__file__).parent
    results_page_path = base_dir / "sample_html" / "results_page.html"

    if not results_page_path.exists():
        logger.error(f"Файл не найден: {results_page_path}")
        return False

    logger.info(f"\n1. ПАРСИНГ СТРАНИЦЫ РЕЗУЛЬТАТОВ")
    logger.info(f"   Файл: {results_page_path}")

    # Инициализируем скрейпер
    scraper = ZakupkiScraper(limit=100)

    # Парсим HTML файл
    tenders = scraper.parse_html_file(str(results_page_path))

    if not tenders:
        logger.error("Ошибка: не распарсено ни одного тендера!")
        return False

    logger.info(f"\n✓ Распарсено тендеров: {len(tenders)}")

    # Выводим первые 3 тендера
    logger.info(f"\n2. ПЕРВЫЕ {min(3, len(tenders))} ТЕНДЕРОВ:")
    for i, tender in enumerate(tenders[:3]):
        print_tender(tender, i + 1)

    # Сохраняем в SQLite
    logger.info(f"\n3. СОХРАНЕНИЕ В БАЗУ ДАННЫХ")
    # Используем /tmp чтобы избежать проблем с доступом
    import tempfile
    tmp_dir = Path(tempfile.gettempdir())
    db_path = tmp_dir / "tenders_test.db"

    try:
        db = TenderDatabase(str(db_path))

        # Удаляем старые данные
        db.delete_all()

        # Добавляем новые тендеры
        for tender in tenders:
            db.insert_tender(tender)

        logger.info(f"✓ Сохранено в БД: {db_path}")

        # Подсчитываем по закону
        logger.info(f"\n4. СТАТИСТИКА")
        all_tenders = db.get_all_tenders()
        fz44_count = sum(1 for t in all_tenders if t['law'] == '44-ФЗ')
        fz223_count = sum(1 for t in all_tenders if t['law'] == '223-ФЗ')
        avg_amount = sum(t['amount'] or 0 for t in all_tenders) / len(all_tenders) if all_tenders else 0

        print(f"\n   Всего тендеров в БД:  {len(all_tenders)}")
        print(f"   44-ФЗ:                {fz44_count}")
        print(f"   223-ФЗ:               {fz223_count}")
        print(f"   Средняя сумма:        {avg_amount:,.0f} руб")

        db.close()

    except Exception as e:
        logger.error(f"Ошибка при работе с БД: {e}")
        return False

    logger.info(f"\n5. ПРОВЕРКА КАЧЕСТВА ПАРСИНГА")

    # Проверяем ключевые поля (обязательные)
    required_fields = ['id', 'title', 'law', 'amount']
    optional_fields = ['customer', 'deadline', 'stage']

    all_required_filled = True
    all_optional_filled = True

    for i, tender in enumerate(tenders):
        missing_required = [f for f in required_fields if not tender.get(f)]
        missing_optional = [f for f in optional_fields if not tender.get(f)]

        if missing_required:
            logger.warning(f"Тендер {i+1} (ID: {tender.get('id')}): отсутствуют ОБЯЗАТЕЛЬНЫЕ поля {missing_required}")
            all_required_filled = False

        if missing_optional:
            logger.debug(f"Тендер {i+1} (ID: {tender.get('id')}): отсутствуют опциональные поля {missing_optional}")
            all_optional_filled = False

    # Оценка качества
    if all_required_filled and len(tenders) >= 2:
        if all_optional_filled:
            logger.info(f"✓ Качество парсинга: ОТЛИЧНО (все поля заполнены для {len(tenders)} тендеров)")
            return True
        else:
            logger.info(f"✓ Качество парсинга: ХОРОШО (обязательные поля заполнены для {len(tenders)} тендеров)")
            return True
    else:
        logger.warning(f"⚠ Качество парсинга: СРЕДНЕЕ (недостающие обязательные поля или мало тендеров)")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
