#!/usr/bin/env python3
"""
Скрипт для генерации схем JSON из снэпшотов тестов.
Этот скрипт используется в GitHub Actions для автоматического создания документации API.
"""

import os
import sys
import glob
import json
import shutil
import argparse
from pathlib import Path


def extract_schemas(snapshots_dir, output_dir):
    """Извлекает схемы JSON из файлов снимков и сохраняет их в отдельные файлы."""
    if not os.path.exists(snapshots_dir):
        print(f"Директория снимков {snapshots_dir} не найдена.")
        return False

    # Создаем выходную директорию, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    # Ищем все файлы схем JSON в директории снимков
    schema_files = glob.glob(os.path.join(snapshots_dir, "*.schema.json"))
    
    if not schema_files:
        print("Файлы схем не найдены в директории снимков.")
        return False
    
    print(f"Найдено {len(schema_files)} файлов схем.")
    
    for schema_file in schema_files:
        try:
            # Копируем файл схемы в выходную директорию
            schema_name = os.path.basename(schema_file)
            output_path = os.path.join(output_dir, schema_name)
            shutil.copy(schema_file, output_path)
            print(f"Скопирован файл схемы: {schema_name}")
        except Exception as e:
            print(f"Ошибка при обработке файла {schema_file}: {str(e)}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Генерация схем JSON из снэпшотов тестов")
    parser.add_argument("snapshots_dir", help="Директория с файлами снимков")
    parser.add_argument("output_dir", help="Директория для выходных файлов схем")
    
    args = parser.parse_args()
    
    if extract_schemas(args.snapshots_dir, args.output_dir):
        print("Схемы успешно извлечены.")
    else:
        print("Ошибка при извлечении схем.")
        sys.exit(1)


if __name__ == "__main__":
    main()
