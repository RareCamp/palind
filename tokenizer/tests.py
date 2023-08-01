import unittest

import tokenizer

class TestSoundex(unittest.TestCase):
    def test_soundex(self):

        self.assertEqual(tokenizer.soundex("Bangalore"), "B524")

        # From PHP docs
        #self.assertEqual(tokenizer.soundex("Euler"), tokenizer.soundex("Ellery")) # E460
        #self.assertEqual(tokenizer.soundex("Gauss"), tokenizer.soundex("Ghosh"))  # G200
        #self.assertEqual(tokenizer.soundex("Hilbert"), tokenizer.soundex("Heilbronn"))  # H416
        #self.assertEqual(tokenizer.soundex("Knuth"), tokenizer.soundex("Kant"))  # K530
        #self.assertEqual(tokenizer.soundex("Lloyd"), tokenizer.soundex("Ladd"))  # L300
        #self.assertEqual(tokenizer.soundex("Lukasiewicz"), tokenizer.soundex("Lissajous"))  # L222

        #self.assertEqual(tokenizer.soundex("Washington"), "W252")
        #self.assertEqual(tokenizer.soundex("Lee"), "L000")
        #self.assertEqual(tokenizer.soundex("Gutierrez"), "G362")
        #self.assertEqual(tokenizer.soundex("Pfister"), "P123") # P236 according to PHP
        #self.assertEqual(tokenizer.soundex("Jackson"), "J250")
        #self.assertEqual(tokenizer.soundex("Tymczak"), "T522")
        #self.assertEqual(tokenizer.soundex("A"), "A000")
        #self.assertEqual(tokenizer.soundex("Çáŕẗéř "), "C636")
        #self.assertEqual(tokenizer.soundex("Ashcroft "), "A261")
        #self.assertEqual(tokenizer.soundex("¿"), "¿000")


if __name__ == '__main__':
    unittest.main()
