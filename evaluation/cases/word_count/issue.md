# word_count miscounts extra spaces and empty text

word_count('hello   world') returns 4 instead of 2, and word_count('') returns 1 instead of 0. Extra whitespace should be ignored.
