# BasiaSzuka

Program przeszukuje pliki HTML w katalogu `input_html` i zapisuje wyniki do katalogu `wyniki`.

[Link do repo](https://github.com/yohirt/html-phrase-search)

## Do czego służy program

Skrypt wyszukuje podane słowa w treści stron HTML i zapisuje:

- liczbę znalezionych trafień,
- zliczenie według każdego szukanego słowa,
- fragment tekstu wokół każdego trafienia,
- numer trafienia na liście wyników,
- globalny numer trafienia we wszystkich przeszukanych plikach,
- które to wystąpienie danego słowa,
- indeks słowa w tekście.

Program szuka tylko całych słów.
To znaczy, że wyszukanie słowa `głowa` nie dopasuje `Głowacka`.

Wyszukiwanie nie rozróżnia wielkości liter.
To znaczy, że `głowa`, `GŁOWA` i `Głowa` są traktowane jako to samo słowo.

## Jak działa program

1. Skrypt odczytuje wszystkie pliki `.html` z katalogu `input_html` i jego podkatalogów.
2. Z każdego pliku usuwa elementy techniczne i poboczne, między innymi:
   `script`, `style`, `head`, `meta`, `link`, `noscript`, `svg`, `nav`, `footer`, `header`, `form`, `button`, `aside`.
3. Jeśli w pliku istnieje znacznik `main`, program przeszukuje przede wszystkim jego treść.
4. Tekst jest dzielony na słowa z zachowaniem polskich znaków.
5. Dla każdego znalezionego słowa program zapisuje kontekst: 50 słów przed i 50 słów po trafieniu.
6. Wyniki są zapisywane do osobnych plików tekstowych w katalogu `wyniki`.

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
1. Szukane słowo: głowa (1. wystąpienie, indeks słowa: 16, globalnie: 37)
znaczenie przejmowania się rzeczami to rodzaj głowa pełna myśli i zmartwień
```

### Wyjaśnienie kolumn:

- **1.** — numer wpisu na liście wyników w danym pliku
- **głowa** — szukane słowo, które zostało znalezione
- **1. wystąpienie** — które to kolejne wystąpienie tego słowa w danym pliku (jeśli słowo pojawi się wielokrotnie, licznik będzie się zwiększać)
- **indeks słowa: 16** — pozycja słowa w tekście po podzieleniu go na słowa
- **globalnie: 37** — kolejne trafienie liczone łącznie przez wszystkie przeszukane pliki (jeśli szukamy kilka słów, każde słowo ma swój globalny licznik)
- **poniżej** — fragment tekstu wokół znalezionego słowa (50 słów przed i 50 słów po trafieniu dla lepszego kontekstu)

### Notatki:

- Program szuka tylko **całych słów** — wyszukanie `głowa` nie dopasuje `głownie` czy `głównie`
- Wyszukiwanie **nie rozróżnia wielkości liter** — `głowa`, `GŁOWA` i `Głowa` są traktowane jako to samo słowo
- Każde szukane słowo ma swój własny licznik globalny (jeśli szukasz `głowa ręka noga`, każde słowo ma oddzielny licznik)

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