import shutil
from pathlib import Path

def setup_frontend():
    # Пути к исходникам и целям
    source = Path("frontend_temp")
    static_dest = Path("static")
    template_dest = Path("templates")

    # Создаем нужные папки, если их нет
    static_dest.mkdir(exist_ok=True)
    template_dest.mkdir(exist_ok=True)

    # 1. Переносим папки со статикой (как на твоем скрине)
    for folder in ["css", "images", "js"]:
        src_folder = source / folder
        if src_folder.exists():
            # Копируем папку целиком внутрь static
            shutil.copytree(src_folder, static_dest / folder, dirs_exist_ok=True)
            print(f"✅ Перенесена папка: {folder}")

    # 2. Переносим HTML-файлы
    for html_file in source.glob("*.html"):
        shutil.copy(html_file, template_dest / html_file.name)
        print(f"📄 Перенесен шаблон: {html_file.name}")

if __name__ == "__main__":
    setup_frontend()