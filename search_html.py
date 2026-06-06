from pathlib import Path
from bs4 import BeautifulSoup
import re
import sys


# ==========================
# KONFIGURACJA
# ==========================

INPUT_DIR = Path("input_html")
OUTPUT_FILE = Path("wyniki.txt")

# Domyślne słowo, jeśli nie podasz go z terminala
DEFAULT_SEARCH_WORD = "programowanie"


# ==========================
# FUNKCJE
# ==========================

def extract_text_from_html(file_path):
    """
    Czyta plik HTML i wyciąga tylko tekst strony.
    Pomija metadane, linki techniczne, style, skrypty, menu, stopki itp.
    """

    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # Usuwamy elementy, których nie chcemy analizować
    unwanted_tags = [
        "script",
        "style",
        "head",
        "meta",
        "link",
        "noscript",
        "svg",
        "nav",
        "footer",
        "header",
        "form",
        "button",
        "aside"
    ]

    for tag in soup(unwanted_tags):
        tag.decompose()

    # Jeżeli strona ma <main>, analizujemy głównie treść z <main>
    main_content = soup.find("main")

    if main_content:
        text = main_content.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)

    # Porządkujemy wielokrotne spacje
    text = re.sub(r"\s+", " ", text)

    return text


def find_fragments(text, word):
    """
    Szuka zdań lub fragmentów zawierających podane słowo.
    """

    # Dzielimy tekst na zdania po kropce, wykrzykniku lub znaku zapytania
    sentences = re.split(r"(?<=[.!?])\s+", text)

    results = []

    for sentence in sentences:
        if word.lower() in sentence.lower():
            results.append(sentence.strip())

    return results


def save_results(results):
    """
    Zapisuje wyniki do pliku tekstowego.
    """

    OUTPUT_FILE.write_text("".join(results), encoding="utf-8")


def main():
    # Jeżeli podasz słowo z terminala, użyje tego słowa
    # np. python search_html.py React
    if len(sys.argv) > 1:
        search_word = " ".join(sys.argv[1:])
    else:
        search_word = DEFAULT_SEARCH_WORD

    print(f"Szukam frazy: {search_word}")

    if not INPUT_DIR.exists():
        print(f"Brak katalogu: {INPUT_DIR}")
        print("Utwórz katalog input_html i wrzuć do niego pliki HTML.")
        return

    html_files = list(INPUT_DIR.rglob("*.html"))

    if not html_files:
        print("Nie znaleziono plików HTML w katalogu input_html.")
        return

    all_results = []

    for html_file in html_files:
        relative_path = html_file.relative_to(INPUT_DIR)
        print(f"Sprawdzam plik: {relative_path}")

        text = extract_text_from_html(html_file)
        fragments = find_fragments(text, search_word)

        if fragments:

            all_results.append(f"\n=== {relative_path} ===\n\n")

            for fragment in fragments:
                all_results.append(f"- {fragment}\n")

    if all_results:
        save_results(all_results)
        print(f"\nGotowe. Wyniki zapisano w pliku: {OUTPUT_FILE}")
    else:
        print("\nNie znaleziono żadnych pasujących fragmentów.")


if __name__ == "__main__":
    main()