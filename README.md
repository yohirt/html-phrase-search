# BasiaSzuka

Program przeszukuje pliki HTML w katalogu `input_html` i zapisuje wyniki do katalogu `wyniki`.

[Link do repo](https://github.com/yohirt/html-phrase-search)

## Do czego służy program

Skrypt wyszukuje podane słowa w treści stron HTML i zapisuje:

- liczbę znalezionych trafień,
- zliczenie według każdego szukanego słowa,
- fragment tekstu wokół każdego trafienia,
- globalny numer trafienia we wszystkich przeszukanych plikach.

Program szuka tylko całych słów.
To znaczy, że wyszukanie słowa `głowa` nie dopasuje `Głowacka`.

Wyszukiwanie nie rozróżnia wielkości liter.
To znaczy, że `głowa`, `GŁOWA` i `Głowa` są traktowane jako to samo słowo.

## Jak działa program

1. Skrypt odczytuje wszystkie pliki `.html` z katalogu `input_html` i jego podkatalogów.
2. Z każdego pliku usuwa elementy techniczne i poboczne, między innymi:
   `script`, `style`, `head`, `meta`, `link`, `noscript`, `svg`, `nav`, `footer`, `header`, `form`, `button`, `aside`.
3. Jeśli w pliku istnieje znacznik `main`, program przeszukuje przede wszystkim jego treść.
4. Tekst jest analizowany słowo po słowie z zachowaniem polskich znaków.
5. Dla każdego znalezionego słowa program zapisuje kontekst: domyślnie 50 słów przed i 50 słów po trafieniu, zachowując oryginalną interpunkcję w wyciętym fragmencie.
6. Wyniki są zapisywane do osobnych plików tekstowych w katalogu `wyniki`.

Liczbę słów pokazywanych przed i po trafieniu można zmienić w zmiennych `WORDS_BEFORE` oraz `WORDS_AFTER` w pliku `search_html.py`.

## Wymagania

- Python 3
- biblioteka `beautifulsoup4`

Instalacja biblioteki:

```bash
pip install beautifulsoup4
```

## Struktura katalogów

Przykładowy układ projektu:

```text
BasiaSzuka/
|-- input_html/
|   |-- strona1/
|   |   `-- preview.html
|-- search_html.py
`-- wyniki/
```

Pliki HTML należy umieszczać w katalogu `input_html`.

## Jak uruchomić program

Uruchom terminal w katalogu projektu i wpisz:

```bash
python search_html.py głowa
```

Aby wyszukać kilka słów naraz:

```bash
python search_html.py głowa ręka noga
```

Jeśli nie podasz żadnego słowa, program użyje domyślnego słowa:

```text
programowanie
```

## Gdzie są zapisywane wyniki

Wyniki trafiają do katalogu `wyniki`.

Program tworzy osobny plik wynikowy dla każdego głównego katalogu znajdującego się wewnątrz `input_html`.

Przykład:

- `input_html/strona1/preview.html` zapisze wynik do pliku `wyniki/strona1.txt`

Jeżeli plik HTML leży bezpośrednio w katalogu `input_html`, wynik trafi do pliku:

```text
wyniki/_glowny_poziom.txt
```

## Jak czytać wynik

Wyniki zapisywane są w formacie tekstowym, gdzie każde znalezione trafienie ma następującą strukturę:

```text
37)
- ... znaczenie przejmowania się rzeczami to rodzaj głowa pełna myśli i zmartwień. To zdanie pozostaje z kropkami, przecinkami i inną interpunkcją tak jak w oryginale ...
```

### Wyjaśnienie kolumn:

- **37)** — kolejne trafienie liczone łącznie przez wszystkie przeszukane pliki
- **linia poniżej** — fragment tekstu wokół znalezionego słowa (domyślnie 50 słów przed i 50 słów po trafieniu dla lepszego kontekstu)
- **interpunkcja i zapis** — fragment zachowuje przecinki, kropki, dwukropki i wielkość liter tak jak w oryginalnym tekście po wyciągnięciu treści z HTML

### Notatki:

- Program szuka tylko **całych słów** — wyszukanie `głowa` nie dopasuje `głownie` czy `głównie`
- Wyszukiwanie **nie rozróżnia wielkości liter** — `głowa`, `GŁOWA` i `Głowa` są traktowane jako to samo słowo
- Licznik wyników jest **wspólny dla wszystkich trafień** i rośnie przez wszystkie przeszukane pliki
- Liczbę słów kontekstu można zmienić w zmiennych `WORDS_BEFORE` i `WORDS_AFTER`

## Co program pomija

Program nie przeszukuje treści znajdujących się w elementach technicznych i nawigacyjnych, takich jak:

- nagłówki strony,
- menu,
- stopki,
- skrypty JavaScript,
- style CSS,
- formularze,
- przyciski,
- elementy boczne.

## Typowe komunikaty

`Brak katalogu: input_html`

Oznacza, że trzeba utworzyć katalog `input_html` i włożyć do niego pliki HTML.

`Nie znaleziono plików HTML w katalogu input_html.`

Oznacza, że katalog istnieje, ale nie ma w nim żadnych plików `.html`.

`Nie znaleziono żadnych pasujących fragmentów.`

Oznacza, że program przejrzał pliki, ale nie znalazł szukanych słów.

## Podsumowanie

Program jest przeznaczony do prostego przeszukiwania treści HTML z pominięciem elementów technicznych strony. Najlepiej sprawdza się wtedy, gdy chcesz szybko znaleźć konkretne słowa w treści wielu plików i dostać gotowe wyniki w plikach tekstowych.