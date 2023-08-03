from collections import defaultdict
from datetime import date
from hashlib import sha256
from math import exp, log
from random import random

import requests


class PIITokenizer:
    def __init__(self, l=1024, eps=3):
        self.l = l
        self.eps = eps
        self.kn = int(l * log(2))  # =~ 0.6931 * l

    #
    # Normalize
    #

    def normalize(self, name, allow_numbers=True):
        name = name.lower()
        name = name.strip()
        name = " ".join(name.split())  # Remove extra whitespace

        allowed_chars = "abcdefghijklmnopqrstuvwxyz" + " "
        if allow_numbers:
            allowed_chars += "0123456789"
        name = "".join([c for c in name if c in allowed_chars])

        return name

    def normalize_date_of_birth(self, date_of_birth):
        return date.fromisoformat(date_of_birth)

    #
    # Validators
    #

    def _validate_gender(self, gender):
        assert gender in ["m", "f"]

    def _validate_country(self, country):
        # TODO: check 2 and 3 letter country codes
        assert country in ["us", "usa"]

    def _validate_state(self, state):
        # TODO: check US states
        pass

    #
    # Tokenizers
    #

    def _tokenize(self, fields):
        # Dynamic number of hash functions
        if fields == [""]:
            return ""
        k = 1 + self.kn // len(set(fields))

        bf = [0] * self.l
        for field in fields:
            for i in range(k):
                hash = sha256(f"{field}#{i}".encode("utf-8")).hexdigest()
                index = int(hash, 16) % self.l
                bf[index] = 1
        eta = 1.0 - 1.0 / (1.0 + exp(self.eps))
        return "".join(map(str, [bit if random() <= eta else 1 - bit for bit in bf]))

    def tokenize(
        self,
        first_name,
        last_name,
        date_of_birth,
        middle_name="",
        gender="",
        city_at_birth="",
        address_at_bith="",
        zip_code_at_birth="",
        abbr_zip_code_at_birth="",
        state_at_birth="",
        country_at_birth="",
    ):
        #
        # Normalize names
        #

        first_name = self.normalize(first_name, allow_numbers=False)
        middle_name = self.normalize(middle_name, allow_numbers=False)
        last_name = self.normalize(last_name, allow_numbers=False)
        gender = self.normalize(gender, allow_numbers=False)
        city_at_birth = self.normalize(city_at_birth, allow_numbers=False)
        address_at_bith = self.normalize(address_at_bith, allow_numbers=True)
        zip_code_at_birth = self.normalize(zip_code_at_birth, allow_numbers=True)
        abbr_zip_code_at_birth = self.normalize(
            abbr_zip_code_at_birth, allow_numbers=True
        )

        #
        # Validate input fields
        #

        if gender:
            self._validate_gender(gender)

        if date_of_birth:
            date_of_birth = self.normalize_date_of_birth(date_of_birth)

        if country_at_birth:
            self._validate_country(country_at_birth)

        if state_at_birth:
            self._validate_state(state_at_birth)

        #
        # Create derived fields
        #

        full_name = self.normalize(f"{first_name}{middle_name}{last_name}")
        first_name_soundex = soundex(first_name)
        last_name_soundex = soundex(last_name)

        #
        # Tokenize
        #

        # Names expanded with bigrams
        first_name_token = self._tokenize(bigrams(first_name))
        middle_name_token = self._tokenize(bigrams(middle_name))
        last_name_token = self._tokenize(bigrams(last_name))
        full_name_token = self._tokenize(bigrams(full_name))

        # Soundex
        first_name_soundex_token = self._tokenize([first_name_soundex])
        last_name_soundex_token = self._tokenize([last_name_soundex])

        # Gender
        gender_token = self._tokenize([gender])

        # Location at birth
        country_at_birth_token = self._tokenize([country_at_birth])
        state_at_birth_token = self._tokenize([state_at_birth])
        city_at_birth_token = self._tokenize(bigrams(city_at_birth))
        zip_code_at_birth_token = self._tokenize([zip_code_at_birth])
        abbr_zip_code_at_birth_token = self._tokenize([abbr_zip_code_at_birth])

        # Date of birth
        date_of_birth_token = self._tokenize([date_of_birth])

        return {
            "first_name_token": first_name_token,
            "middle_name_token": middle_name_token,
            "last_name_token": last_name_token,
            "full_name_token": full_name_token,
            "first_name_soundex_token": first_name_soundex_token,
            "last_name_soundex_token": last_name_soundex_token,
            "gender_token": gender_token,
            "country_at_birth_token": country_at_birth_token,
            "state_at_birth_token": state_at_birth_token,
            "city_at_birth_token": city_at_birth_token,
            "zip_code_at_birth_token": zip_code_at_birth_token,
            "abbr_zip_code_at_birth_token": abbr_zip_code_at_birth_token,
            "date_of_birth_token": date_of_birth_token,
        }

    def submit(self, url, dataset_api_token, token):
        return requests.post(
            url,
            headers={
                "Authorization": f"Bearer {dataset_api_token}",
                "Content-Type": "application/json",
            },
            json=token,
        )


# Q-grams


def bigrams(s):
    if len(s) == 0:
        return [""]
    if len(s) == 1:
        return [s + ":1"]
    if len(s) == 2:
        return [s + ":1", s[0] + ":1", s[1] + ":1"]

    times_seen = defaultdict(int)
    grams = []
    for i in range(len(s) - 1):
        gram = s[i : i + 2]
        times_seen[gram] += 1
        grams += [f"{gram}:{times_seen[gram]}"]

    return grams


def soundex(token):
    """Source: https://www.geeksforgeeks.org/implement-phonetic-search-in-python-with-soundex-algorithm/"""
    token = token.upper()
    soundex = ""

    # Retain the First Letter
    soundex += token[0]

    # Create a dictionary which maps
    # letters to respective soundex
    # codes. Vowels and 'H', 'W' and
    # 'Y' will be represented by '.'
    dictionary = {
        "BFPV": "1",
        "CGJKQSXZ": "2",
        "DT": "3",
        "L": "4",
        "MN": "5",
        "R": "6",
        "AEIOUHWY": ".",
    }

    # Enode as per the dictionary
    for char in token[1:]:
        for key in dictionary.keys():
            if char in key:
                code = dictionary[key]
                if code != ".":
                    if code != soundex[-1]:
                        soundex += code

    # Trim or Pad to make Soundex a
    # 4-character code
    # print(soundex)
    soundex = soundex[:4].ljust(4, "0")

    return soundex
