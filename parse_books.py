import time
import random
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def iterate_pages(start_url):
    parsed = urlparse(start_url)
    query = parse_qs(parsed.query)

    if "p" not in query:
        raise ValueError("В URL нет параметра p")

    page = int(query["p"][0])

    while True:
        query["p"] = [str(page)]
        yield urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
        page += 1


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    content = soup.select_one("#content")
    if not content:
        return None

    # Убираем заведомо мусорные теги
    for tag in content.find_all(["script", "style", "iframe"]):
        tag.decompose()

    # Убираем навигационные ссылки
    for a in content.find_all("a"):
        a.unwrap()   # важно: unwrap, а не decompose

    text = content.get_text("\n", strip=True)

    # Remove service rows
    bad_lines = (
        "Читать онлайн",
        "Следующая страница",
        "Предыдущая страница",
        "Комментарии",
        "🔢 Страница",
        "Вернуться к просмотру книги",
        "Перейти к Оглавлению",
        "Реклама",
        "…",
        "−",
        "+"
    )

    bad_starts = (
        "📃 Cтраница",
        "Книги автора:",
        "Серия:",
        "Онлайн книга",
        "[",
        "Вернуться к просмотру книги"
    )

    titles = (
        "глава",
    )

    lines = []

    for line in text.splitlines():
        if any(line.lower().startswith(title) for title in titles):
            lines.append("\n" + line + "\n")
#        elif not any(bad in line for bad in bad_lines) and not line.isdigit() and not any(line.startswith(bad) for bad in bad_starts):
        elif not any(line in bad for bad in bad_lines) and not line.isdigit() and not any(line.startswith(bad) for bad in bad_starts):

            lines.append(line)


    clean_text = "\n".join(lines).strip()

    if len(clean_text) < 200:
        return None

    return clean_text


def polite_sleep():
    time.sleep(random.uniform(0.9, 1.6))


def parse_book(start_url, out_file="/home/maint/Projects/Parse_books/books/trudnosti_perevoda_s_drakonevo.txt"):
    session = create_session()
    seen_hashes = set()
    pages_count = 0

    with open(out_file, "w", encoding="utf-8") as f:
        for url in iterate_pages(start_url):
            print("Читаем:", url)

            r = session.get(url, timeout=10)
            if r.status_code != 200:
                print("Page error - Stoped")
                break

            text = extract_text(r.text)
            if not text:
                print("Text not found - Stoped")
                break

            h = text_hash(text)
            if h in seen_hashes:
                print("Page repeated - End of the book")
                break

            seen_hashes.add(h)

            f.write(text)
            f.write("\n\n")

            pages_count += 1
            polite_sleep()

    print(f"Done. Saved pages: {pages_count}")



if __name__ == "__main__":
    parse_book("https://loveread.ec/read_book.php?id=115958&p=1")
