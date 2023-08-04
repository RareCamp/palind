from datetime import date
import unittest

import linker


class TestSimilarity(unittest.TestCase):
    def test_similarity(self):
        self.assertRaises(AssertionError, linker.similarity, "", "")
        self.assertRaises(AssertionError, linker.similarity, "0", "11")

        self.assertEqual(linker.similarity("0", "1"), 0.0)
        self.assertEqual(linker.similarity("1", "0"), 0.0)
        self.assertEqual(linker.similarity("0", "0"), 1.0)
        self.assertEqual(linker.similarity("1", "1"), 1.0)

        self.assertEqual(linker.similarity("00", "00"), 1.0)
        self.assertEqual(linker.similarity("10", "00"), 0.5)
        self.assertEqual(linker.similarity("01", "00"), 0.5)
        self.assertEqual(linker.similarity("11", "00"), 0.0)

        self.assertEqual(linker.similarity("0000", "0000"), 1.0)
        self.assertEqual(linker.similarity("1000", "0000"), 0.75)
        self.assertEqual(linker.similarity("1100", "0000"), 0.5)
        self.assertEqual(linker.similarity("1110", "0000"), 0.25)

        self.assertEqual(linker.similarity("0" * 1000, "1" * 1000), 0.0)
        self.assertEqual(linker.similarity("1" * 1000, "1" * 1000), 1.0)
        self.assertEqual(linker.similarity("10" * 1000, "11" * 1000), 0.5)


if __name__ == "__main__":
    unittest.main()
