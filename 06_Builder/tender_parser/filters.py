"""
Фильтры и нормализация данных для тендеров.
"""
import logging
from typing import Optional
from config import STOP_KEYWORDS

logger = logging.getLogger(__name__)


def has_stop_keyword(text: str) -> bool:
    """
    Проверяет, содержит ли текст стоп-слова (авиа, воздушные перевозки).

    Args:
        text: Текст для проверки (обычно title)

    Returns:
        True если найдено стоп-слово, False иначе
    """
    if not text:
        return False

    text_lower = text.lower()
    for keyword in STOP_KEYWORDS:
        if keyword.lower() in text_lower:
            logger.debug(f"Найдено стоп-слово '{keyword}' в '{text}'")
            return True

    return False


def normalize_amount(amount_str: Optional[str]) -> Optional[int]:
    """
    Пытается распарсить сумму НМЦ из строки.

    Args:
        amount_str: Строка с суммой (может быть '1 234 567.89 руб' или похоже)

    Returns:
        Целое число рублей или None
    """
    if not amount_str:
        return None

    try:
        # Убираем пробелы, запятые, текст (руб, рублей, и т.д.)
        cleaned = amount_str.lower().replace("руб", "").replace(",", ".")
        cleaned = "".join(c for c in cleaned if c.isdigit() or c in ".,-")
        cleaned = cleaned.replace(" ", "")

        # Парсим как float, потом int
        value = float(cleaned)
        return int(value)
    except (ValueError, AttributeError) as e:
        logger.warning(f"Не удалось распарсить сумму '{amount_str}': {e}")
        return None


def normalize_deadline(deadline_str: Optional[str]) -> Optional[str]:
    """
    Нормализует дату deadline. Пока просто возвращает как есть.

    Args:
        deadline_str: Строка даты

    Returns:
        Нормализованная строка или None
    """
    if not deadline_str:
        return None
    return deadline_str.strip()


def normalize_title(title: str) -> str:
    """
    Нормализует заголовок (убирает лишние пробелы).

    Args:
        title: Заголовок тендера

    Returns:
        Очищенный заголовок
    """
    return " ".join(title.split())
