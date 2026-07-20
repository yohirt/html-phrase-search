from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


# ==========================
# KONFIGURACJA
# ==========================

INPUT_DIR = Path("input_html")
OUTPUT_DIR = Path("wyniki")

# Domyślne słowo, jeśli nie podasz go z terminala.
DEFAULT_SEARCH_WORDS = ["programowanie"]

# Ile słów przed i po znalezionym słowie pokazać.
WORDS_BEFORE = 50
WORDS_AFTER = 50

WORD_PATTERN = re.compile(r"\b[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+\b", flags=re.UNICODE)
VALID_NUMERIC_CHARREF_PATTERN = re.compile(r"&#(?:x[0-9a-fA-F]+|\d+);")
BROKEN_NUMERIC_CHARREF_PATTERN = re.compile(r"&#[^\s<;]*;?")


def sanitize_numeric_charrefs(html):
    """
    Dekoduje poprawne encje numeryczne i usuwa uszkodzone.

    Niektóre strony zawierają fragmenty typu &#x... z niepoprawnymi znakami.
    Standardowy parser HTML potrafi wtedy przerwać analizę tekstu.
    """

    def decode_match(match):
        value = match.group(0)[2:-1]

        try:
            if value.lower().startswith("x"):
                return chr(int(value[1:], 16))

            return chr(int(value, 10))
        except (OverflowError, ValueError):
            return " "

    html = VALID_NUMERIC_CHARREF_PATTERN.sub(decode_match, html)
    return BROKEN_NUMERIC_CHARREF_PATTERN.sub(" ", html)


class VisibleTextParser(HTMLParser):
    """
    Wyciąga tekst widoczny dla użytkownika.

    Parser działa z convert_charrefs=False, żeby wadliwe encje HTML nie
    przerywały działania programu.
    """

    unwanted_tags = {
        "script",
        "style",
        "head",
        "noscript",
        "svg",
        "nav",
        "footer",
        "header",
        "form",
        "button",
        "aside",
    }

    # Tagi puste (void elements) nie mają znaczników zamykających. Nie mogą
    # zwiększać _ignored_depth, bo po np. <link> parser ignorowałby całą
    # pozostałą część dokumentu. Nie zawierają tekstu, więc nie trzeba ich
    # dodawać do unwanted_tags.

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._ignored_depth = 0
        self._main_depth = 0
        self._all_text_parts = []
        self._main_text_parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in self.unwanted_tags:
            self._ignored_depth += 1

        if tag == "main" and self._ignored_depth == 0:
            self._main_depth += 1

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "main" and self._main_depth > 0:
            self._main_depth -= 1

        if tag in self.unwanted_tags and self._ignored_depth > 0:
            self._ignored_depth -= 1

    def handle_data(self, data):
        self._append_text(unescape(data))

    def handle_entityref(self, name):
        self._append_text(unescape(f"&{name};"))

    def handle_charref(self, name):
        try:
            if name.lower().startswith("x"):
                value = chr(int(name[1:], 16))
            else:
                value = chr(int(name, 10))
        except (OverflowError, ValueError):
            value = " "

        self._append_text(value)

    def _append_text(self, text):
        if self._ignored_depth > 0 or not text:
            return

        self._all_text_parts.append(text)

        if self._main_depth > 0:
            self._main_text_parts.append(text)

    def get_text(self):
        parts = self._main_text_parts or self._all_text_parts
        return re.sub(r"\s+", " ", " ".join(parts)).strip()


# ==========================
# FUNKCJE
# ==========================

def extract_text_from_html(file_path):
    """
    Czyta plik HTML i wyciąga tylko tekst strony.
    Pomija metadane, linki techniczne, style, skrypty, menu, stopki itp.
    """

    html = file_path.read_text(encoding="utf-8", errors="ignore")
    html = sanitize_numeric_charrefs(html)
    parser = VisibleTextParser()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def split_text_into_words(text):
    """
    Dzieli tekst na słowa.
    Zachowuje polskie znaki.
    """

    return WORD_PATTERN.findall(text)


def normalize_word(word):
    """
    Zamienia słowo na małe litery do porównywania.
    """

    return word.lower()


def expand_fragment_bounds_to_punctuation(text, start, end):
    """
    Rozszerza granice fragmentu o interpunkcję, która faktycznie przylega
    do skrajnych słów. Niczego nie dopisuje.
    """

    while start > 0 and not text[start - 1].isspace() and not re.match(r"\w", text[start - 1], flags=re.UNICODE):
        start -= 1

    while end < len(text) and not text[end].isspace() and not re.match(r"\w", text[end], flags=re.UNICODE):
        end += 1

    return start, end


def find_fragments(text, search_words):
    """
    Szuka całych słów.
    Dla każdego znalezienia zwraca 50 słów przed i 50 słów po,
    zachowując oryginalną interpunkcję i zapis fragmentu.
    """

    word_matches = list(WORD_PATTERN.finditer(text))
    results = []
    match_counts = Counter()

    normalized_search_words = [normalize_word(word) for word in search_words]

    for index, match in enumerate(word_matches):
        current_word = match.group(0)
        normalized_current_word = normalize_word(current_word)

        if normalized_current_word in normalized_search_words:
            match_counts[normalized_current_word] += 1
            start_word_index = max(0, index - WORDS_BEFORE)
            end_word_index = min(len(word_matches) - 1, index + WORDS_AFTER)

            fragment_start = word_matches[start_word_index].start()
            fragment_end = word_matches[end_word_index].end()
            fragment_start, fragment_end = expand_fragment_bounds_to_punctuation(text, fragment_start, fragment_end)
            fragment = text[fragment_start:fragment_end].strip()

            results.append({
                "word": current_word,
                "word_occurrence": match_counts[normalized_current_word],
                "word_index": index + 1,
                "fragment": fragment,
            })

    return results


def get_main_folder(relative_path):
    """
    Zwraca nazwę głównego katalogu w input_html.

    Przykład:
    input_html/strona1/o-nas/index.html
    zwróci:
    strona1

    Jeżeli plik HTML leży bezpośrednio w input_html,
    trafia do pliku _glowny_poziom.txt.
    """

    if len(relative_path.parts) > 1:
        return relative_path.parts[0]

    return "_glowny_poziom"


def safe_filename(name):
    """
    Czyści nazwę pliku wynikowego.
    """

    name = re.sub(r"[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+", "_", name, flags=re.UNICODE)
    return name.strip("_")


def save_results_by_main_folder(results_by_folder):
    """
    Zapisuje wyniki osobno dla każdego głównego katalogu.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)

    for folder_name, results in results_by_folder.items():
        output_file = OUTPUT_DIR / f"{safe_filename(folder_name)}.txt"
        output_file.write_text("".join(results), encoding="utf-8")


def main():
    # Przykład:
    # python search_html.py głowa ręka noga
    if len(sys.argv) > 1:
        search_words = sys.argv[1:]
    else:
        search_words = DEFAULT_SEARCH_WORDS

    print("Szukam słów:")
    for word in search_words:
        print(f"- {word}")

    if not INPUT_DIR.exists():
        print(f"\nBrak katalogu: {INPUT_DIR}")
        print("Utwórz katalog input_html i wrzuć do niego katalogi z plikami HTML.")
        return

    html_files = list(INPUT_DIR.rglob("*.html"))

    if not html_files:
        print("\nNie znaleziono plików HTML w katalogu input_html.")
        return

    results_by_folder = {}
    total_matches = 0
    total_counts_by_word = Counter()
    global_match_number = 0

    for html_file in html_files:
        relative_path = html_file.relative_to(INPUT_DIR)
        main_folder = get_main_folder(relative_path)

        print(f"Sprawdzam plik: {relative_path}")

        text = extract_text_from_html(html_file)
        fragments = find_fragments(text, search_words)

        if fragments:
            if main_folder not in results_by_folder:
                results_by_folder[main_folder] = []

            match_count = len(fragments)
            total_matches += match_count
            counts_by_word = Counter(normalize_word(item["word"]) for item in fragments)
            total_counts_by_word.update(counts_by_word)

            results_by_folder[main_folder].append(f"\n=== PLIK: {relative_path} ===\n\n")

            for search_word in search_words:
                normalized_search_word = normalize_word(search_word)
                word_count = counts_by_word.get(normalized_search_word, 0)
                # results_by_folder[main_folder].append(f"- {search_word}: {word_count}\n")

            results_by_folder[main_folder].append("\n")

            for item in fragments:
                global_match_number += 1
                fragment = item["fragment"]

                results_by_folder[main_folder].append(
                    f"{global_match_number})\n"
                )
                results_by_folder[main_folder].append(f"- ... {fragment} ...\n\n")

    if results_by_folder:
        save_results_by_main_folder(results_by_folder)

        print("\nGotowe. Wyniki zapisano w katalogu:")
        print(OUTPUT_DIR)
        print(f"\nŁączna liczba znalezionych słów: {total_matches}")

        print("\nZliczenie według słów:")
        for search_word in search_words:
            normalized_search_word = normalize_word(search_word)
            word_count = total_counts_by_word.get(normalized_search_word, 0)
            print(f"- {search_word}: {word_count}")

        print("\nUtworzone pliki:")
        for folder_name in results_by_folder:
            print(f"- {OUTPUT_DIR / (safe_filename(folder_name) + '.txt')}")
    else:
        print("\nNie znaleziono żadnych pasujących fragmentów.")


if __name__ == "__main__":
    main()
