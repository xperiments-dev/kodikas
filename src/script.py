import re


def func(a: int, b: int) -> int:
    return a + b


def hello() -> str:
    return "hello world"


def boooom(a={}):
    return "hello"


def special_characters_in_string() -> bool:
    string = "boooo"
    regex_pattern = re.compile("[@_!#$%^&'*()<>?/\|}\"{~:=]")

    if regex_pattern.search(string):
        return True
    return False


# ------------------

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from typing import Any, List


start = time()

print("*******")


def boo(hello: List[Any]=[]) -> bool:
    with ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(special_characters_in_string))
        futures.append(executor.submit(special_characters_in_string))
        for future in as_completed(futures):
            print(future.result())
    return special_characters_in_string()
