import PIITokenizer from './tokenizer';

describe('PIITokenizer', () => {
    let tokenizer;

    beforeEach(() => {
        tokenizer = new PIITokenizer();
    });

    test('normalize method should remove non-alphanumeric characters', () => {
        const input = 'John Doe!';
        const expectedOutput = 'john doe';
        expect(tokenizer.normalize(input)).toBe(expectedOutput);
    });

    // Add more tests here for other methods
    test('end to end tokenization', async () => {
        const firstName = 'John';
        const lastName = 'Doe';
        const dateOfBirth = '1990-01-01';
        const middleName = 'A';
        const formerName = 'Smith';
        const gender = 'M';
        const output = await tokenizer.tokenize({
            firstName: firstName,
            lastName: lastName,
            dateOfBirth: dateOfBirth,
            middleName: middleName,
            formerName: formerName,
            gender: gender
        });
    });

    test('soundex', () => {
        expect(tokenizer.soundex("Bangalore")).toBe("B524");

        // From PHP docs
        expect(tokenizer.soundex("Euler")).toBe(tokenizer.soundex("Ellery"));  // E460
        expect(tokenizer.soundex("Gauss")).toBe(tokenizer.soundex("Ghosh"));  // G200
        expect(tokenizer.soundex("Hilbert")).toBe(tokenizer.soundex("Heilbronn"));  // H416
        expect(tokenizer.soundex("Knuth")).toBe(tokenizer.soundex("Kant"));  // K530
        expect(tokenizer.soundex("Lloyd")).toBe(tokenizer.soundex("Ladd"));  // L300
        expect(tokenizer.soundex("Lukasiewicz")).toBe(tokenizer.soundex("Lissajous"));  // L222

        expect(tokenizer.soundex("Washington")).toBe("W252");
        expect(tokenizer.soundex("Lee")).toBe("L000");
        expect(tokenizer.soundex("Gutierrez")).toBe("G362");
        expect(tokenizer.soundex("Pfister")).toBe("P123");  // P236 according to PHP
        expect(tokenizer.soundex("Jackson")).toBe("J250");
        expect(tokenizer.soundex("Tymczak")).toBe("T520");  // T522 depending on the implementation
        expect(tokenizer.soundex("A")).toBe("A000");
        // expect(tokenizer.soundex("Çáŕẗéř ")).toBe("C636");  // Our implementation does not support unicode
        expect(tokenizer.soundex("Ashcroft ")).toBe("A261");
        expect(tokenizer.soundex("¿")).toBe("¿000");
    });

    test('expand', () => {
        expect(tokenizer.expand("hello")).toEqual(["he:1", "el:1", "ll:1", "lo:1"]);
        expect(tokenizer.expand("")).toEqual([""]);
        expect(tokenizer.expand("a")).toEqual(["a:1"]);
        expect(tokenizer.expand("ab")).toEqual(["ab:1", "a:1", "b:1"]);
        expect(tokenizer.expand("abc")).toEqual(["ab:1", "bc:1", "a:1", "b:1", "c:1"]);
        expect(tokenizer.expand("aab")).toEqual(["aa:1", "ab:1", "a:1", "a:2", "b:1"]);
        expect(tokenizer.expand("aaa")).toEqual(["aa:1", "aa:2", "a:1", "a:2", "a:3"]);
        expect(tokenizer.expand("aaaa")).toEqual(["aa:1", "aa:2", "aa:3"]);
        expect(tokenizer.expand("barbara")).toEqual(["ba:1", "ar:1", "rb:1", "ba:2", "ar:2", "ra:1"]);
        expect(tokenizer.expand("he llo")).toEqual(["he:1", "e :1", " l:1", "ll:1", "lo:1"]);
    });

    test('qGrams', () => {
        expect(tokenizer.qGrams("hello", 1)).toEqual(["h", "e", "l", "l", "o"]);
        expect(tokenizer.qGrams("hello", 2)).toEqual(["he", "el", "ll", "lo"]);
        expect(tokenizer.qGrams("hello", 3)).toEqual(["hel", "ell", "llo"]);
        expect(tokenizer.qGrams("hello", 4)).toEqual(["hell", "ello"]);
        expect(tokenizer.qGrams("hello", 5)).toEqual(["hello"]);
        expect(tokenizer.qGrams("hello", 6)).toEqual([]);

        expect(tokenizer.qGrams("aa", 1)).toEqual(["a", "a"]);
    });
});

