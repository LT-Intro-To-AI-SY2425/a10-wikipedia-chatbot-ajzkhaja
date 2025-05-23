import re, string
import wikipedia
from bs4 import BeautifulSoup
from match import match
from typing import List, Callable, Tuple, Any, Match

# === Helper Functions ===

def get_page_html(title: str) -> str:
    results = wikipedia.search(title)
    return wikipedia.page(results[0]).html()

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

# === Wikipedia Data Extraction Functions ===

def get_capital_of_country(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"Capital.*?(?:\n|:)?\s*([A-Z][a-zA-Z]*(?: [A-Z][a-zA-Z]*)?)"
    match = get_match(infobox_text, pattern, "No capital found")
    return match.group(1).strip()

def get_population_of_country(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"Population.*?([\d]{2,3}(?:,\d{3})+)"
    match = get_match(infobox_text, pattern, "No population found")
    return match.group(1).replace(",", "")

def get_motto_of_country(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"Motto\s*(?:\"|“)?([^\"]+)"
    match = get_match(infobox_text, pattern, "No motto found")
    return match.group(1).strip()

def get_president_of_country(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"President.*?([A-Z][a-z]+ [A-Z][a-z]+)"
    match = get_match(infobox_text, pattern, "No president found")
    return match.group(1).strip()

def get_prime_minister_of_country(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"Prime Minister.*?([A-Z][a-z]+ [A-Z][a-z]+)"
    match = get_match(infobox_text, pattern, "No prime minister found")
    return match.group(1).strip()

# === Action Wrappers ===

def capital_city(matches: List[str]) -> List[str]:
    return [get_capital_of_country(" ".join(matches))]

def population(matches: List[str]) -> List[str]:
    return [get_population_of_country(" ".join(matches))]

def motto(matches: List[str]) -> List[str]:
    return [get_motto_of_country(" ".join(matches))]

def president(matches: List[str]) -> List[str]:
    return [get_president_of_country(" ".join(matches))]

def prime_minister(matches: List[str]) -> List[str]:
    return [get_prime_minister_of_country(" ".join(matches))]

def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt

# === Pattern/Action List ===

Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

pa_list: List[Tuple[Pattern, Action]] = [
    ("what is the capital of %".split(), capital_city),
    ("what is the population of %".split(), population),
    ("what is the motto of %".split(), motto),
    ("who is the president of %".split(), president),
    ("who is the prime minister of %".split(), prime_minister),
    (["bye"], bye_action),
]

# === Main Logic ===

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


