import re, string
import wikipedia
from bs4 import BeautifulSoup
from match import match
from typing import List, Callable, Tuple, Any, Match

#  Helper Functions 

def get_page_html(title: str) -> str:
    results = wikipedia.search(title)
    if not results:
        raise ValueError(f"No Wikipedia page found for '{title}'. Check spelling.")
    return wikipedia.page(results[0], auto_suggest=False).html()

def get_first_infobox_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")
    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text

def clean_text(text: str) -> str:
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    return no_dup_spaces

def get_match(text: str, pattern: str, error_text: str = "Pattern not found") -> Match:
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)
    if not match:
        raise AttributeError(error_text)
    return match

#  Wikipedia Data Extraction Functions 

def get_population_of_country(country: str) -> str:
    html = get_page_html(country)
    infobox_text = clean_text(get_first_infobox_text(html))
    pattern = r"Population[^\n]*?([1-9]\d{5,})"
    match = get_match(infobox_text, pattern, "No population found")
    return match.group(1)

def get_area_of_country(country: str) -> str:
    html = get_page_html(country)
    infobox_text = clean_text(get_first_infobox_text(html))
    pattern = r"Area.*?([\d]{1,3}(?:,\d{3})+\s*km2)"
    match = get_match(infobox_text, pattern, "No area found")
    return match.group(1).strip()

def get_language_of_country(country: str) -> str:
    html = get_page_html(country)
    infobox_text = clean_text(get_first_infobox_text(html))
    pattern = r"Official language[s]?(?:\s*\(.*?\))?\s*[:\-]?\s*([A-Za-z ,]+)"
    match = get_match(infobox_text, pattern, "No official language found")
    return match.group(1).strip()

#  matches down bwlow

def population(matches: List[str]) -> List[str]:
    return [get_population_of_country(" ".join(matches))]

def area(matches: List[str]) -> List[str]:
    return [get_area_of_country(" ".join(matches))]

def language(matches: List[str]) -> List[str]:
    return [get_language_of_country(" ".join(matches))]

def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt

#  Pattern/Action List 

Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

pa_list: List[Tuple[Pattern, Action]] = [
    ("what is the population of %".split(), population),
    ("what is the area of %".split(), area),
    ("what is the official language of %".split(), language),
    ("what are the official languages of %".split(), language),
    (["bye"], bye_action),
]

#  Main Logic 

def search_pa_list(src: List[str]) -> List[str]:
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]
    return ["I don't understand"]

def query_loop() -> None:
    print("Welcome to the Wikipedia chatbot!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)
        except (KeyboardInterrupt, EOFError):
            break
    print("\nSo long!\n")

# Run Chatbot
query_loop()

