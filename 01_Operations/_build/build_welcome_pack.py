#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт сборки Welcome Pack для Татьяны (диспетчер, 1 мая 2026)
Объединяет 5 md-файлов в единый PDF с обложкой, оглавлением и нумерацией страниц.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Конфигурация
BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "Welcome_Pack_Tatyana_2026-05-01.pdf"

# Список файлов в правильном порядке
SOURCE_FILES = [
    "Dispatcher_Welcome_Doc.md",
    "Dispatcher_Job_Description.md",
    "Dispatcher_Bonus_Scheme.md",
    "Dispatcher_Escalation_Map.md",
    "Carrier_Audit_Checklist.md"
]

def create_cover_page():
    """Создаёт Markdown для обложки"""
    cover = """---
title: Welcome Pack
subtitle: Татьяна — диспетчер
author: Тихоокеанская звезда / Логистика Дальнего Востока
date: 1 мая 2026
---

\\begin{titlepage}
\\centering
\\vspace*{\\baselineskip}
\\rule{\\textwidth}{1.6pt}\\vspace*{-\\baselineskip}\\vspace*{2pt}
\\rule{\\textwidth}{0.4pt}\\\\[\\baselineskip]
\\Huge{\\textbf{Welcome Pack}}\\\\[1.5cm]
{\\large Татьяна — диспетчер}\\\\[2cm]
{\\normalsize Тихоокеанская звезда}\\\\
{\\normalsize Логистика Дальнего Востока}\\\\[\\baselineskip]
\\rule{\\textwidth}{0.4pt}\\vspace*{-\\baselineskip}\\vspace{3.2pt}
\\rule{\\textwidth}{1.6pt}\\\\[3cm]
\\vfill
{Дата выхода: 1 мая 2026}\\\\
{Версия: апрель 2026}
\\end{titlepage}

\\newpage
"""
    return cover

def read_source_file(filepath):
    """Читает исходный md-файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️  Файл не найден: {filepath}")
        return ""

def main():
    """Основная логика сборки"""

    print("=" * 60)
    print("СБОРКА Welcome Pack для Татьяны")
    print("=" * 60)

    # Проверяем наличие исходных файлов
    print("\n1️⃣  Проверка исходных файлов...")
    missing_files = []
    for fname in SOURCE_FILES:
        fpath = BASE_DIR / fname
        if not fpath.exists():
            missing_files.append(fname)
            print(f"   ❌ {fname} — НЕ НАЙДЕН")
        else:
            fsize = fpath.stat().st_size
            print(f"   ✅ {fname} ({fsize} байт)")

    if missing_files:
        print(f"\n⚠️  ОШИБКА: не найдены файлы: {missing_files}")
        sys.exit(1)

    # Собираем единый Markdown документ
    print("\n2️⃣  Объединение документов...")
    combined_md = create_cover_page()

    # Добавляем каждый файл
    for fname in SOURCE_FILES:
        fpath = BASE_DIR / fname
        content = read_source_file(fpath)
        combined_md += content
        combined_md += "\n\n\\newpage\n\n"

    # Записываем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                      delete=False, encoding='utf-8') as tmp:
        tmp.write(combined_md)
        tmp_file = tmp.name

    print(f"   ✅ Объединено {len(SOURCE_FILES)} документов")

    # Генерируем PDF через pandoc + xelatex
    print("\n3️⃣  Генерация PDF (pandoc + xelatex)...")

    cmd = [
        'pandoc',
        tmp_file,
        '-o', str(OUTPUT_FILE),
        '--pdf-engine=xelatex',
        '--variable', 'mainfont=DejaVu Sans',
        '--variable', 'documentclass=report',
        '--number-sections',
        '--toc',
        '--toc-depth=2',
        '-V', 'geometry:left=20mm,right=20mm,top=25mm,bottom=25mm',
        '-V', 'linestretch=1.15',
        '-V', 'pagestyle=headings',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            print(f"   ❌ Ошибка pandoc:")
            print(result.stderr)
            sys.exit(1)

        print(f"   ✅ PDF создан успешно")

    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)

    # Проверяем результат
    if OUTPUT_FILE.exists():
        pdf_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)

        print("\n" + "=" * 60)
        print("✅ УСПЕШНО!")
        print("=" * 60)
        print(f"Файл: {OUTPUT_FILE}")
        print(f"Размер: {pdf_size_mb:.2f} МБ")
        print(f"Готово к раздаче Татьяне в первый день (1 мая 2026)")

    else:
        print(f"   ❌ Ошибка: файл не создан")
        sys.exit(1)

if __name__ == '__main__':
    main()
