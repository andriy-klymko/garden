import csv
import re
import sys

FILE_PATH = "Data/trees.csv"

ALLOWED_STATUSES = {"прижилося", "посаджено", "сумнівно", "засохло"}
ALLOWED_PLOTS = {"main", "house"}
# Формат: M-R1..M-R7, H-H, H-G, H-R1, H-R2 з обов'язковим .M та числом метрів
ID_PATTERN = re.compile(r"^(M-R[1-7]|H-[GH]|H-R[1-3])\.M\d+(\.\d+)?$")

errors = []
ids = set()

try:
    with open(FILE_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        required_cols = {"tree_id", "plot", "row", "distance_m", "crop", "status"}
        if not required_cols.issubset(reader.fieldnames or []):
            errors.append(f"Помилка заголовків: відсутні обов'язкові колонки {required_cols - set(reader.fieldnames or [])}")

        for line_num, row in enumerate(reader, start=2):
            tree_id = row.get("tree_id", "").strip()
            plot = row.get("plot", "").strip()
            status = row.get("status", "").strip()
            dist = row.get("distance_m", "").strip()

            # 1. Перевірка ID
            if not tree_id:
                errors.append(f"Рядок {line_num}: відсутній tree_id")
            elif not ID_PATTERN.match(tree_id):
                errors.append(f"Рядок {line_num}: некоректний формат tree_id '{tree_id}' (очікується за схемою data/SCHEMA.md)")
            elif tree_id in ids:
                errors.append(f"Рядок {line_num}: дублікат tree_id '{tree_id}'")
            ids.add(tree_id)

            # 2. Перевірка plot
            if plot not in ALLOWED_PLOTS:
                errors.append(f"Рядок {line_num} ({tree_id}): недозволене значення plot '{plot}'")

            # 3. Перевірка distance_m
            try:
                val = float(dist)
                if val < 0:
                    errors.append(f"Рядок {line_num} ({tree_id}): відстань не може бути від'ємною ({dist})")
            except ValueError:
                errors.append(f"Рядок {line_num} ({tree_id}): відстань '{dist}' не є числом")

            # 4. Перевірка status
            if status not in ALLOWED_STATUSES:
                errors.append(f"Рядок {line_num} ({tree_id}): неприпустимий статус '{status}'. Дозволені: {ALLOWED_STATUSES}")

except FileNotFoundError:
    errors.append(f"Файл {FILE_PATH} не знайдено!")

if errors:
    print(f"❌ ЗНАЙДЕНО ПОМИЛОК: {len(errors)}")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)  # Завершення з кодом помилки для зупинки GitHub Action
else:
    print(f"✅ Успішно! Перевірено {len(ids)} записів. Реєстр trees.csv повністю відповідає специфікації.")
    sys.exit(0)