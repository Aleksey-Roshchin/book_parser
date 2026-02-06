import os
import time
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_log(log, msg):
    if log:
        log(msg)


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    content = soup.select_one("#content")
    if not content:
        return None

    for tag in content.find_all(["script", "style", "iframe"]):
        tag.decompose()

    for a in content.find_all("a"):
        a.unwrap()

    raw_text = content.get_text("\n", strip=True)

    bad_contains = (
        "Читать онлайн",
        "Следующая страница",
        "Предыдущая страница",
        "Комментарии",
        "Реклама",
        "Вернуться к просмотру книги",
        "Перейти к Оглавлению",
    )

    bad_starts = (
        "📃 Cтраница",
        "Книги автора:",
        "Серия:",
        "Онлайн книга",
        "[",
    )

    titles = ("глава",)

    lines = []

    for line in raw_text.splitlines():
        line = line.strip()

        if not line:
            continue

        # служебные строки целиком
        if line in ("…", "−", "+"):
            continue

        # заголовки
        if any(line.lower().startswith(t) for t in titles):
            lines.append("\n" + line + "\n")
            continue

        if (
            any(bad in line for bad in bad_contains)
            or any(line.startswith(bad) for bad in bad_starts)
            or line.isdigit()
        ):
            continue

        lines.append(line)

    clean_text = "\n".join(lines).strip()

    if len(clean_text) < 200:
        return None

    return clean_text



def parse_book(start_url, save_dir, log=None, delay=1.0):
    session = requests.Session()
    session.headers.update(HEADERS)

    page = 1
    prev_text = None
    full_text = []

    safe_log(log, "Старт парсинга")

    while True:
        url = start_url.replace("p=1", f"p={page}")
        safe_log(log, f"Читаем страницу {page}")

        resp = session.get(url, timeout=15)
        resp.raise_for_status()

        text = extract_text(resp.text)

        if not text:
            safe_log(log, "Текст не найден — стоп")
            break

        if text == prev_text:
            safe_log(log, "Текст повторился — конец книги")
            break

        full_text.append(text)
        prev_text = text
        page += 1

        time.sleep(delay)

    if not full_text:
        raise RuntimeError("Книга не была загружена")

    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, "book.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_text))

    safe_log(log, f"Готово! Файл сохранён: {filename}")

    return filename
