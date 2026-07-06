# BasiaSzuka

Program przeszukuje pliki HTML w katalogu `input_html` i zapisuje wyniki do katalogu `wyniki`.

## Do czego służy program

Skrypt wyszukuje podane słowa w treści stron HTML i zapisuje:

- fragment tekstu wokół każdego trafienia,
- globalny numer trafienia we wszystkich przeszukanych plikach,
- zliczenie według każdego szukanego słowa.

Program szuka tylko całych słów. Wyszukanie słowa `głowa` nie dopasuje więc `Głowacka`.
Wyszukiwanie nie rozróżnia wielkości liter.

## Jak działa program

1. Skrypt odczytuje wszystkie pliki `.html` z katalogu `input_html` i jego podkatalogów.
2. Pomija elementy techniczne i poboczne, między innymi `script`, `style`, `head`, `nav`, `footer`, `header`, `form`, `button` i `aside`.
3. Jeżeli w pliku istnieje znacznik `main`, program przeszukuje przede wszystkim jego treść.
4. Tekst jest analizowany słowo po słowie z zachowaniem polskich znaków.
5. Dla każdego znalezionego słowa program zapisuje kontekst: domyślnie 50 słów przed i 50 słów po trafieniu.
6. Wyniki są zapisywane do osobnych plików tekstowych w katalogu `wyniki`.

Skrypt używa tylko biblioteki standardowej Pythona. Nie trzeba instalować dodatkowych pakietów.

## Struktura katalogów

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
python search_html.py Wojnicz Nauczyciel informatyki
```

Aby wyszukać inne słowa:

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

Wyniki zapisywane są w formacie tekstowym:

```text
37)
- ... fragment tekstu przed znalezionym słowem i po znalezionym słowie ...
```

Liczbę słów pokazywanych przed i po trafieniu można zmienić w zmiennych `WORDS_BEFORE` oraz `WORDS_AFTER` w pliku `search_html.py`.

## Typowe komunikaty

`Brak katalogu: input_html`

Oznacza, że trzeba utworzyć katalog `input_html` i włożyć do niego pliki HTML.

`Nie znaleziono plików HTML w katalogu input_html.`

Oznacza, że katalog istnieje, ale nie ma w nim żadnych plików `.html`.

`Nie znaleziono żadnych pasujących fragmentów.`

Oznacza, że program przejrzał pliki, ale nie znalazł szukanych słów.
