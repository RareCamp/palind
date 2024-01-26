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
        console.log(output);
    });
});
