#!/usr/bin/env python3
"""
MVP парсер тендеров для закупки.gov.ru.
Точка входа, запуск парсинга и сохранение в БД.
"""
import logging
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from scraper import run_scraper
from storage import TenderDB
from config import DEFAULT_LIMIT, DB_PATH

# Настройка логирования
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция парсера."""
    parser = argparse.ArgumentParser(
        description="Парсер тендеров для закупки.gov.ru",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python parser.py                    # По умолчанию: 50 тендеров, headless режим
  python parser.py --limit 100        # Парсить 100 тендеров
  python parser.py --headful          # Видимое окно браузера (для отладки)
  python parser.py --db-path /tmp/my.db --limit 10
        """,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Количество тендеров для парсинга (по умолчанию {DEFAULT_LIMIT})",
    )

    parser.add_argument(
        "--headful",
        action="store_true",
        help="Запустить браузер в видимом режиме (для отладки)",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default=DB_PATH,
        help=f"Путь к файлу SQLite БД (по умолчанию {DB_PATH})",
    )

    args = parser.parse_args()

    logger.info(f"Запуск парсера с параметрами: limit={args.limit}, headful={args.headful}, db_path={args.db_path}")

    try:
        # Инициализируем БД
        db = TenderDB(db_path=args.db_path)
        logger.info(f"БД инициализирована: {args.db_path}")

        # Запускаем скрейпер
        logger.info("Запуск скрейпера...")
        headless = not args.headful
        tenders = run_scraper(headless=headless, limit=args.limit)

        logger.info(f"Скрейпер завершён. Найдено тендеров: {len(tenders)}")

        if not tenders:
            logger.warning("Тендеры не найдены. Проверьте структуру сайта и фильтры.")
            print("\n=== РЕЗУЛЬТАТЫ ===")
            print(f"Найдено всего: 0")
            print(f"Добавлено новых: 0")
            return

        # Сохраняем в БД и подсчитываем новые
        new_count = 0
        for tender in tenders:
            if db.upsert_tender(tender):
                new_count += 1

        logger.info(f"Сохранено в БД: {new_count} новых, {len(tenders) - new_count} обновлено")

        # Получаем топ-10 новых по сумме
        top_tenders = db.get_recent_new_tenders(limit=10)

        # Выводим результаты
        print("\n" + "=" * 100)
        print("=== РЕЗУЛЬТАТЫ ПАРСИНГА ТЕНДЕРОВ ===")
        print("=" * 100)
        print(f"\nНайдено всего: {len(tenders)}")
        print(f"Добавлено новых: {new_count}")
        print(f"Всего в БД: {db.get_tender_count()}\n")

        if top_tenders:
            print("-" * 100)
            print("ТОП-10 НОВЫХ ТЕНДЕРОВ ПО СУММЕ:")
            print("-" * 100)

            for idx, tender in enumerate(top_tenders, 1):
                amount_str = f"{tender['amount']:,} руб" if tender["amount"] else "N/A"
                print(f"\n{idx}. ID: {tender['id']}")
                print(f"   Заголовок: {tender['title']}")
                print(f"   Сумма НМЦ: {amount_str}")
                print(f"   Срок подачи: {tender['deadline'] or 'N/A'}")
                print(f"   Ссылка: {tender['link']}")

            print("\n" + "=" * 100)

    except KeyboardInterrupt:
        logger.info("Парсер прерван пользователем")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
