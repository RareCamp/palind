
const MAX_UINT32 = Math.pow(2, 32) - 1;

async function cryptoRandom() {
    return crypto.getRandomValues(new Uint32Array(1))[0] / MAX_UINT32;
}

async function tokenizeChunks(chunks, l = 1024, eps = 3.0, eta = null) {
    const kn = Math.floor(l * Math.log(2));  // =~ 0.6931 * l

    // Dynamic number of hash functions
    const k = 1 + Math.floor(kn / new Set(chunks).size);

    const bf = Array(l).fill(0);
    for (const field of chunks) {
        for (let i = 0; i < k; i++) {
            const hash = crypto.createHash('sha256').update(`${field}#${i}`).digest('hex');
            const index = parseInt(hash, 16) % l;
            bf[index] = 1;
        }
    }

    if (eta === null) {  // eta = probability of keeping the bit the same
        eta = 1.0 - 1.0 / (1.0 + Math.exp(eps));
    }
    return bf.map(bit => cryptoRandom() <= eta ? bit : 1 - bit).join('');
}

class PIITokenizer {
    constructor() {
        this.l = 1024;
        this.epsilons = {
            "firstName": 3.0,
            "firstNameSoundex": 3.0,
            "lastName": 3.0,
            "lastNameSoundex": 3.0,
            "middleName": 3.0,
            "fullName": 3.0,
            "dateOfBirth": 0.4,
            "formerName": 3.0,
            "sexAtBirth": 0.2,
            "cityAtBirth": 3.0,
            "addressAtBirth": 3.0,
            "zipCodeAtBirth": 0.4,
            "stateAtBirth": 0.2,
            "countryAtBirth": 0.2,
            "parent1FirstName": 3.0,
            "parent1LastName": 3.0,
            "parent1FullName": 3.0,
            "parent1Email": 3.0,
            "parent2FirstName": 3.0,
            "parent2LastName": 3.0,
            "parent2FullName": 3.0,
            "parent2Email": 3.0
        }
    }

    normalize(name, allowNumbers = true) {
        name = name.normalize("NFD");                 // Convert string to Normalized Form Decomposed
        name = name.replace(/[\u0300-\u036f]/g, "");  // Remove diacritics
        name = name.trim();                           // Remove leading and trailing whitespace
        name = name.split(/\s+/).join(' ');           // Remove repeated whitespace
        name = name.toLowerCase();                    // Convert to lowercase

        // Remove non-alphanumeric characters
        let allowedChars = 'abcdefghijklmnopqrstuvwxyz ';
        if (allowNumbers) {
            allowedChars += '0123456789';
        }
        name = Array.from(name).filter(c => allowedChars.includes(c)).join('');

        return name;
    }

    normalizeName(name) {
        return this.normalize(name, false);
    }

    normalizeDateOfBirth(dateOfBirth) {
        return new Date(dateOfBirth).toISOString().slice(0, 10); // YYYY-MM-DD
    }

    validateGender(gender) {
        if (!['m', 'f'].includes(gender)) {
            throw new Error('Invalid gender');
        }
    }

    validateCountry(country) {
        if (!['us', 'usa'].includes(country)) {
            throw new Error('Invalid country');
        }
    }

    validateState(state) {
        // TODO: check US states
    }

    validateEmail(email) {
        let emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            throw new Error('Invalid email');
        }
    }

    async tokenizeField(fieldName, chunks) {
        if (chunks.length === 1 && chunks[0] === '') {
            return '';
        }

        return await tokenizeChunks(chunks, this.l, this.epsilons[fieldName]);
    }

    async tokenize({
        firstName,
        lastName,
        dateOfBirth,
        middleName = '',
        formerName = '',
        gender = '',
        email = '',
        cityAtBirth = '',
        addressAtBirth = '',
        zipCodeAtBirth = '',
        stateAtBirth = '',
        countryAtBirth = '',
        parent1FirstName = '',
        parent1LastName = '',
        parent1Email = '',
        parent2FirstName = '',
        parent2LastName = '',
        parent2Email = '',
    } = {}) {
        // Normalize names
        firstName = this.normalizeName(firstName);
        middleName = this.normalizeName(middleName);
        lastName = this.normalizeName(lastName);
        formerName = this.normalizeName(formerName);
        parent1FirstName = this.normalizeName(parent1FirstName);
        parent1LastName = this.normalizeName(parent1LastName);
        parent2FirstName = this.normalizeName(parent2FirstName);
        parent2LastName = this.normalizeName(parent2LastName);
        gender = this.normalizeName(gender);
        cityAtBirth = this.normalizeName(cityAtBirth);

        // Fields with allowed numbers
        addressAtBirth = this.normalize(addressAtBirth, true);
        zipCodeAtBirth = this.normalize(zipCodeAtBirth, true);

        // Emails are just stripped from whitespace
        email = email.trim();
        parent1Email = parent1Email.trim();
        parent2Email = parent2Email.trim();

        // Validate input fields
        if (email) {
            this.validateEmail(email);
        }
        // TODO: parents emails

        if (gender) {
            this.validateGender(gender);
        }

        if (dateOfBirth) {
            dateOfBirth = this.normalizeDateOfBirth(dateOfBirth);
        }

        if (countryAtBirth) {
            this.validateCountry(countryAtBirth);
        }

        if (stateAtBirth) {
            this.validateState(stateAtBirth);
        }

        // Create derived fields
        let fullName = this.normalize(`${firstName}${middleName}${lastName}`);
        let firstNameSoundex = this.soundex(firstName);
        let lastNameSoundex = this.soundex(lastName);

        let parent1FullName = this.normalize(`${parent1FirstName}${parent1LastName}`);
        let parent2FullName = this.normalize(`${parent2FirstName}${parent2LastName}`);

        // Tokenize

        // Names expanded with bigrams
        let firstNameToken = await this.tokenizeField("firstName", this.expand(firstName));
        let middleNameToken = await this.tokenizeField("middleName", this.expand(middleName));
        let lastNameToken = await this.tokenizeField("lastName", this.expand(lastName));
        let fullNameToken = await this.tokenizeField("fullName", this.expand(fullName));
        let parent1FirstNameToken = await this.tokenizeField("parent1FirstName", this.expand(parent1FirstName));
        let parent1LastNameToken = await this.tokenizeField("parent1LastName", this.expand(parent1LastName));
        let parent2FirstNameToken = await this.tokenizeField("parent2FirstName", this.expand(parent2FirstName));
        let parent2LastNameToken = await this.tokenizeField("parent2LastName", this.expand(parent2LastName));
        let parent1FullNameToken = await this.tokenizeField("parent1FullName", this.expand(parent1FullName));
        let parent2FullNameToken = await this.tokenizeField("parent2FullName", this.expand(parent2FullName));

        // Emails are not expanded
        let emailToken = await this.tokenizeField("email", [email]);
        let parent1EmailToken = await this.tokenizeField("parent1Email", [parent1Email]);
        let parent2EmailToken = await this.tokenizeField("parent2Email", [parent2Email]);

        // Soundex
        let firstNameSoundexToken = await this.tokenizeField("firstNameSoundex", [firstNameSoundex]);
        let lastNameSoundexToken = await this.tokenizeField("lastNameSoundex", [lastNameSoundex]);
        let parent1FirstNameSoundexToken = await this.tokenizeField("parent1FirstNameSoundex", [this.soundex(parent1FirstName)]);
        let parent1LastNameSoundexToken = await this.tokenizeField("parent1LastNameSoundex", [this.soundex(parent1LastName)]);
        let parent2FirstNameSoundexToken = await this.tokenizeField("parent2FirstNameSoundex", [this.soundex(parent2FirstName)]);
        let parent2LastNameSoundexToken = await this.tokenizeField("parent2LastNameSoundex", [this.soundex(parent2LastName)]);

        // Gender
        let genderToken = await this.tokenizeField("gender", [gender]);

        // Location at birth
        let countryAtBirthToken = await this.tokenizeField("countryAtBirth", [countryAtBirth]);
        let stateAtBirthToken = await this.tokenizeField("stateAtBirth", [stateAtBirth]);
        let cityAtBirthToken = await this.tokenizeField("cityAtBirth", this.expand(cityAtBirth));
        let zipCodeAtBirthToken = await this.tokenizeField("zipCodeAtBirth", [zipCodeAtBirth]);

        // Date of birth
        let dateOfBirthToken = await this.tokenizeField("dateOfBirth", [dateOfBirth]);

        return {
            // Name
            "firstNameToken": firstNameToken,
            "middleNameToken": middleNameToken,
            "lastNameToken": lastNameToken,
            "fullNameToken": fullNameToken,
            "firstNameSoundexToken": firstNameSoundexToken,
            "lastNameSoundexToken": lastNameSoundexToken,
            // Email
            "emailToken": emailToken,
            // Gender
            "genderToken": genderToken,
            // Location at birth
            "countryAtBirthToken": countryAtBirthToken,
            "stateAtBirthToken": stateAtBirthToken,
            "cityAtBirthToken": cityAtBirthToken,
            "zipCodeAtBirthToken": zipCodeAtBirthToken,
            "dateOfBirthToken": dateOfBirthToken,
            // Parental information
            "parent1FirstNameToken": parent1FirstNameToken,
            "parent1LastNameToken": parent1LastNameToken,
            "parent1FullNameToken": parent1FullNameToken,
            "parent1FirstNameSoundexToken": parent1FirstNameSoundexToken,
            "parent1LastNameSoundexToken": parent1LastNameSoundexToken,
            "parent1EmailToken": parent1EmailToken,
            "parent2FirstNameToken": parent2FirstNameToken,
            "parent2LastNameToken": parent2LastNameToken,
            "parent2FullNameToken": parent2FullNameToken,
            "parent2FirstNameSoundexToken": parent2FirstNameSoundexToken,
            "parent2LastNameSoundexToken": parent2LastNameSoundexToken,
            "parent2EmailToken": parent2EmailToken,
        };
    }

    async submit(base_url = 'app.palind.io', datasetApiToken, tokens) {
        const response = await fetch(base_url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${datasetApiToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tokens),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    soundex(s) {
        s = s.toUpperCase();

        if (s === "") {
            return "0000";
        }

        let soundex = "";

        // Retain the First Letter
        soundex += s[0];

        // Create a dictionary which maps
        // letters to respective soundex
        // codes. Vowels and 'H', 'W', and
        // 'Y' will be represented by '.'
        const dictionary = {
            "BFPV": "1",
            "CGJKQSXZ": "2",
            "DT": "3",
            "L": "4",
            "MN": "5",
            "R": "6",
            "AEIOUHWY": ".",
        };

        // Encode as per the dictionary
        for (let i = 1; i < s.length; i++) {
            for (let key in dictionary) {
                if (key.includes(s[i])) {
                    let code = dictionary[key];
                    if (code !== ".") {
                        if (s[i] != s[i - 1] && code !== soundex[soundex.length - 1]) {
                            soundex += code;
                        }
                    }
                }
            }
        }

        // Trim or Pad to make Soundex a
        // 4-character code
        soundex = soundex.slice(0, 4).padEnd(4, "0");

        return soundex;
    }

    expand(s) {
        let grams;
        if (s.length === 0) {
            return [''];
        } else if (s.length === 1) {
            grams = [s];
        } else if (s.length <= 3) {
            grams = [...this.qGrams(s, 2), ...this.qGrams(s, 1)];
        } else {
            grams = this.qGrams(s, 2);
        }

        const counter = {};
        const timesSeen = g => (counter[g] = (counter[g] || 0) + 1);
        return grams.map(g => `${g}:${timesSeen(g)}`);
    }

    qGrams(s, q = 2) {
        if (s.length < q) {
            return [];
        }
        else if (s.length == q) {
            return [s];
        }
        const grams = [];
        for (var i = 0; i < s.length - q + 1; i++) {
            grams.push(s.slice(i, i + q));
        }
        return grams;
    }
}

