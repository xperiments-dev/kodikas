import re


def func(a, b):
    return a + b


def hello():
    return "hello world"


def special_characters_in_string():
    string = "boooo"
    regex_pattern = re.compile("[@_!#$%^&'*()<>?/\|}\"{~:=]")

    if regex_pattern.search(string):
        return True
    return False


# ------------------

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time


start = time()


def boo(hello=[]):
    with ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(special_characters_in_string))
        futures.append(executor.submit(special_characters_in_string))
        for future in as_completed(futures):
            print(future.result())
    return special_characters_in_string()


# test code
