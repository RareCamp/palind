from collections import Counter
from datetime import date
from hashlib import sha256
from math import exp, log
from random import random

import requests


class PIITokenizer:
    def __init__(self, l=1024, eps=3):
        self.l = l
        self.eps = eps

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

    def normalize_name(self, name):
        return self.normalize(name, allow_numbers=False)

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

    def _validate_email(self, email):
        # TODO: check email
        pass

    def _validate_omim(self, omim):
        # TODO: check OMIM
        pass

    #
    # Tokenizers
    #

    def _tokenize(self, fields):
        if fields == [""]:
            return ""

        return tokenize(fields, self.l, self.eps)

    def tokenize(
        self,
        first_name,
        last_name,
        date_of_birth,
        middle_name="",
        former_name="",
        gender="",
        email="",
        city_at_birth="",
        address_at_bith="",
        zip_code_at_birth="",
        abbr_zip_code_at_birth="",
        state_at_birth="",
        country_at_birth="",
        # Parental information
        parent1_first_name="",
        parent1_last_name="",
        parent1_email="",
        parent2_first_name="",
        parent2_last_name="",
        parent2_email="",
        # OMIM
        gene_name="",
        omim="",
    ):
        #
        # Normalize names
        #

        first_name = self.normalize_name(first_name)
        middle_name = self.normalize_name(middle_name)
        last_name = self.normalize_name(last_name)
        former_name = self.normalize_name(former_name)
        parent1_first_name = self.normalize_name(parent1_first_name)
        parent1_last_name = self.normalize_name(parent1_last_name)
        parent2_first_name = self.normalize_name(parent2_first_name)
        parent2_last_name = self.normalize_name(parent2_last_name)
        gender = self.normalize_name(gender)
        city_at_birth = self.normalize_name(city_at_birth)

        # Fields with allowed numbers
        address_at_bith = self.normalize(address_at_bith, allow_numbers=True)
        zip_code_at_birth = self.normalize(zip_code_at_birth, allow_numbers=True)
        abbr_zip_code_at_birth = self.normalize(
            abbr_zip_code_at_birth, allow_numbers=True
        )

        # Emails are just striped from whitespace
        email = email.strip()
        parent1_email = parent1_email.strip()
        parent2_email = parent2_email.strip()

        #
        # Validate input fields
        #

        if email:
            self._validate_email(email)
        # TODO: parents emails

        if gender:
            self._validate_gender(gender)

        if date_of_birth:
            date_of_birth = self.normalize_date_of_birth(date_of_birth)

        if country_at_birth:
            self._validate_country(country_at_birth)

        if state_at_birth:
            self._validate_state(state_at_birth)

        if omim:
            self._validate_omim(omim)

        #
        # Create derived fields
        #

        full_name = self.normalize(f"{first_name}{middle_name}{last_name}")
        first_name_soundex = soundex(first_name)
        last_name_soundex = soundex(last_name)

        parent1_full_name = self.normalize(f"{parent1_first_name}{parent1_last_name}")
        parent2_full_name = self.normalize(f"{parent2_first_name}{parent2_last_name}")

        #
        # Tokenize
        #

        # Names expanded with bigrams
        first_name_token = self._tokenize(expand(first_name))
        middle_name_token = self._tokenize(expand(middle_name))
        last_name_token = self._tokenize(expand(last_name))
        full_name_token = self._tokenize(expand(full_name))
        parent1_first_name_token = self._tokenize(expand(parent1_first_name))
        parent1_last_name_token = self._tokenize(expand(parent1_last_name))
        parent2_first_name_token = self._tokenize(expand(parent2_first_name))
        parent2_last_name_token = self._tokenize(expand(parent2_last_name))
        parent1_full_name_token = self._tokenize(expand(parent1_full_name))
        parent2_full_name_token = self._tokenize(expand(parent2_full_name))

        # Emails are not expanded
        email_token = self._tokenize([email])
        parent1_email_token = self._tokenize([parent1_email])
        parent2_email_token = self._tokenize([parent2_email])

        # Soundex
        first_name_soundex_token = self._tokenize([first_name_soundex])
        last_name_soundex_token = self._tokenize([last_name_soundex])
        parent1_first_name_soundex_token = self._tokenize([soundex(parent1_first_name)])
        parent1_last_name_soundex_token = self._tokenize([soundex(parent1_last_name)])
        parent2_first_name_soundex_token = self._tokenize([soundex(parent2_first_name)])
        parent2_last_name_soundex_token = self._tokenize([soundex(parent2_last_name)])

        # Gender
        gender_token = self._tokenize([gender])

        # Location at birth
        country_at_birth_token = self._tokenize([country_at_birth])
        state_at_birth_token = self._tokenize([state_at_birth])
        city_at_birth_token = self._tokenize(expand(city_at_birth))
        zip_code_at_birth_token = self._tokenize([zip_code_at_birth])
        abbr_zip_code_at_birth_token = self._tokenize([abbr_zip_code_at_birth])

        # Date of birth
        date_of_birth_token = self._tokenize([date_of_birth])

        # OMIM
        omim_token = self._tokenize([omim])

        return {
            "first_name_token": first_name_token,
            "middle_name_token": middle_name_token,
            "last_name_token": last_name_token,
            "full_name_token": full_name_token,
            "first_name_soundex_token": first_name_soundex_token,
            "last_name_soundex_token": last_name_soundex_token,
            "email_token": email_token,
            "gender_token": gender_token,
            "country_at_birth_token": country_at_birth_token,
            "state_at_birth_token": state_at_birth_token,
            "city_at_birth_token": city_at_birth_token,
            "zip_code_at_birth_token": zip_code_at_birth_token,
            "abbr_zip_code_at_birth_token": abbr_zip_code_at_birth_token,
            "date_of_birth_token": date_of_birth_token,
            # Parental information
            "parent1_first_name_token": parent1_first_name_token,
            "parent1_last_name_token": parent1_last_name_token,
            "parent1_full_name_token": parent1_full_name_token,
            "parent1_first_name_soundex_token": parent1_first_name_soundex_token,
            "parent1_last_name_soundex_token": parent1_last_name_soundex_token,
            "parent1_email_token": parent1_email_token,
            "parent2_first_name_token": parent2_first_name_token,
            "parent2_last_name_token": parent2_last_name_token,
            "parent2_full_name_token": parent2_full_name_token,
            "parent2_first_name_soundex_token": parent2_first_name_soundex_token,
            "parent2_last_name_soundex_token": parent2_last_name_soundex_token,
            "parent2_email_token": parent2_email_token,
            # OMIM
            "omim_token": omim_token,
        }

    def submit(self, url, dataset_api_token, token):
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {dataset_api_token}",
                "Content-Type": "application/json",
            },
            json=token,
        )
        response.raise_for_status()
        return response.json()

    def columns(self):
        return list(self.tokenize("", "", "").keys())


def tokenize(fields, l=1024, eps=3.0, eta=None):
    kn = int(l * log(2))  # =~ 0.6931 * l

    # Dynamic number of hash functions
    k = 1 + kn // len(set(fields))

    bf = [0] * l
    for field in fields:
        for i in range(k):
            hash = sha256(f"{field}#{i}".encode("utf-8")).hexdigest()
            index = int(hash, 16) % l
            bf[index] = 1

    if eta is None:  # eta = probability of keeping the bit the same
        eta = 1.0 - 1.0 / (1.0 + exp(eps))
    return "".join(map(str, [bit if random() <= eta else 1 - bit for bit in bf]))


# Q-grams


def q_grams(s, q):
    return [s[i : i + q] for i in range(len(s) - q + 1)]


def expand(s):
    """
    Expand a string with q-grams, counting the number of times each q-gram appears.
    - Empty strings are expanded to [""].
    - Strings of length 1 are expanded to ["s:1"].
    - Strings of length 2 and 3 are expanded with q-grams of size 1 and 2: "aab" -> ["aa:1", "ab:1", "a:1", "a:2", "b:1"]
    - Strings of length 4 or more are expanded with q-grams of size 2: "hello" -> ["he:1", "el:1", "ll:1", "lo:1"]
    """
    if len(s) == 0:
        return [""]
    elif len(s) == 1:
        grams = [s]
    elif len(s) <= 3:
        grams = q_grams(s, 2) + q_grams(s, 1)
    else:
        grams = q_grams(s, 2)

    counter = Counter()
    times_seen = lambda g: counter.update([g]) or counter[g]
    return [f"{g}:{times_seen(g)}" for g in grams]


def soundex(token):
    """Source: https://www.geeksforgeeks.org/implement-phonetic-search-in-python-with-soundex-algorithm/"""
    token = token.upper()
    soundex = ""

    if token == "":
        return "0000"

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
    soundex = soundex[:4].ljust(4, "0")

    return soundex
