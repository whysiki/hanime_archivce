import unittest
import os
from path_tools import ensure_file_exists


class TestEnsureFileExists(unittest.TestCase):

    def test_existing_file(self):
        # Call the function
        result = ensure_file_exists("test.txt")
        # Check that the function returned True
        self.assertTrue(result[0])
        # Remove the file
        os.remove("test.txt")

    def test_non_existing_file_in_directory(self):
        # Call the function with a file path that includes a directory
        result = ensure_file_exists("test__/test.txt")
        # Check that the function returned True
        self.assertTrue(result[0])
        # Remove the file and directory
        os.remove("test__/test.txt")
        os.rmdir("test__")

    def test_non_existing_file_in_mitiple_directory(self):
        # Call the function with a file path that includes a directory
        result = ensure_file_exists("test__/test__/test__/test.txt")
        # Check that the function returned True
        self.assertTrue(result[0])
        # Remove the file and directory
        os.remove("test__/test__/test__/test.txt")
        os.rmdir("test__/test__/test__")
        os.rmdir("test__/test__")
        os.rmdir("test__")

    def test_invalid_filepath_type(self):
        # Call the function with an invalid filepath type (int)
        result = ensure_file_exists(1)
        result2 = ensure_file_exists(set())
        # Check that the function returned False
        self.assertFalse(result[0])
        self.assertFalse(result2[0])

    def test_none_filepath(self):
        # Call the function with None as the filepath
        result = ensure_file_exists(None)
        # Check that the function returned False
        self.assertFalse(result[0])


if __name__ == "__main__":
    unittest.main()
