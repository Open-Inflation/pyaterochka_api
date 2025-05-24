import os
import glob
import sys

# Путь к директории с документацией
docs_dir = sys.argv[1] if len(sys.argv) > 1 else "docs"
if not os.path.exists(docs_dir):
    print(f"Директория {docs_dir} не найдена. Проверьте путь к директории.")
    sys.exit(1)

# Получаем список HTML файлов
html_files = glob.glob(os.path.join(docs_dir, "*.html"))

# Создаем содержимое индексной страницы
index_content = """<!DOCTYPE html>
<html>
<head>
    <title>API Pyaterochka - Документация</title>
    <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Overpass:300,400,600,800">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="schema_doc.css">
    <style>
        body { padding: 20px; font-family: 'Overpass', sans-serif; }
        h1 { margin-bottom: 30px; }
        .schema-list { margin-top: 20px; }
        .footer { margin-top: 30px; text-align: center; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>API Pyaterochka - Документация</h1>
        <div class="schema-list">
            <h2>Доступные схемы:</h2>
            <ul class="list-group">
"""

# Добавляем ссылки на каждую схему
for html_file in sorted(html_files):
    if "index.html" in html_file:
        continue
    
    file_name = os.path.basename(html_file)
    schema_name = file_name.replace(".schema.html", "").replace("_", " ").title()
    
    index_content += f'                <li class="list-group-item"><a href="{file_name}">{schema_name}</a></li>\n'

# Завершаем HTML документ
index_content += """            </ul>
        </div>
        <div class="footer">
            <p>Документация автоматически сгенерирована из схем JSON. Последнее обновление: <span id="last-update"></span></p>
            <script>
                document.getElementById('last-update').textContent = new Date().toLocaleDateString();
            </script>
        </div>
    </div>
    <script src="schema_doc.min.js"></script>
</body>
</html>
"""

# Записываем индексную страницу
with open(os.path.join(docs_dir, "index.html"), "w") as f:
    f.write(index_content)

print("Индексная страница сгенерирована!")