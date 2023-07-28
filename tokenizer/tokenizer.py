from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from math import exp, log

import numpy as np


class PIITokenizer:
    def __init__(self, l, k, eps):
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

    #
    # Validators
    #

    def _validate_gender(self, gender):
        assert gender in ["m", "f"]

    def _validate_date_of_birth(self, date_of_birth):
        # TODO
        assert date_of_birth != ""

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
        k = 1 + self.kn // len(set(fields))

        bf = [0] * self.l
        for field in fields:
            for i in range(k):
                hash = sha256(f"{field}#{i}".encode("utf-8")).hexdigest()
                index = int(hash, 16) % self.l
                bf[index] = 1
        eta = 1.0 - 1.0 / (1.0 + exp(self.eps))
        return np.array(
            [bit if np.random.random() <= eta else 1 - bit for bit in bf], dtype=np.uint8
        )

    def tokenize(self,
            first_name="",
            middle_name="",
            last_name="",
            gender="",
            date_of_birth="",
            city_at_birth="",
            address_at_bith="",
            state_at_birth="",
            country_at_birth="",
            zip_code_at_birth="",
            abbr_zip_code_at_birth=""):

        # Require first, last and dob

        #
        # Normalize names
        #

        first_name = self.normalize(first_name, allow_numbers=False)
        middle_name = self.normalize(middle_name, allow_numbers=False)
        last_name = self.normalize(last_name, allow_numbers=False)
        gender = self.normalize(gender, allow_numbers=False)
        city_at_birth = self.normalize(city_at_birth, allow_numbers=False)
        address_at_bith = self.normalize(address_at_bith, allow_numbers=True)

        #
        # Validate input fields
        #

        if gender:
            self._validate_gender(gender)
        
        if date_of_birth:
            self._validate_date_of_birth(date_of_birth)

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
        first_name_token = self._tokenize(self.q_grams(first_name))
        middle_name_token = self._tokenize(self.q_grams(middle_name))
        last_name_token = self._tokenize(self.q_grams(last_name))
        full_name_token = self._tokenize(self.q_grams(full_name))

        # Soundex
        first_name_soundex_token = self._tokenize([first_name_soundex])
        last_name_soundex_token = self._tokenize([last_name_soundex])

        # Gender
        gender_token = self._tokenize([gender])

        # Location at birth
        country_at_birth_token = self._tokenize([country_at_birth])
        state_at_birth_token = self._tokenize([state_at_birth])
        city_at_birth_token = self._tokenize(self.q_grams([city_at_birth]))
        zip_code_at_birth_token = self._tokenize([zip_code_at_birth])
        abbr_zip_code_at_birth_token = self._tokenize([abbr_zip_code_at_birth])


        # Date of birth
        date_of_birth_token = self._tokenize([date_of_birth])

        return {
            "first_name": first_name_token,
            "middle_name": middle_name_token,
            "last_name": last_name_token,
            "full_name": full_name_token,
            "first_name_soundex": first_name_soundex_token,
            "last_name_soundex": last_name_soundex_token,
            "gender": gender_token,
            "country_at_birth": country_at_birth_token,
            "state_at_birth": state_at_birth_token,
            "city_at_birth": city_at_birth_token,
            "date_of_birth": date_of_birth_token,
        }


# Q-grams


def q_grams(s, q=2, prefix=""):
    if len(s) < q:
        return [s] + list(s)

    times_seen = defaultdict(int)
    grams = []
    for i in range(len(s) - q + 1):
        gram = s[i : i + q]
        times_seen[gram] += 1
        grams += [f"{prefix}{gram}:{times_seen[gram]}"]

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
                if code != '.':
                    if code != soundex[-1]:
                        soundex += code

    # Trim or Pad to make Soundex a
    # 4-character code
    print(soundex)
    soundex = soundex[:4].ljust(4, "0")

    return soundex

