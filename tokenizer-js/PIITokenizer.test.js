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
});

describe('Soundex', () => {
    let tokenizer;

    beforeEach(() => {
        tokenizer = new PIITokenizer();
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
});