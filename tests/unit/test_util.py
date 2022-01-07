"""Tests for the lambda_bundler.util module."""
import os
import pathlib
import shutil
import tempfile
import unittest

from unittest.mock import patch

import lambda_bundler.util as target_module

class UtilTestCases(unittest.TestCase):
    """Test cases for the util module"""

    def setUp(self):
        self.module = "lambda_bundler.util."

    def test_hash_string(self):
        """Asserts hash_string returns the correct sha256 hexdigest"""

        test_string = "test"
        expected_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

        self.assertEqual(expected_hash, target_module.hash_string(test_string))

    def test_get_content_of_files(self):
        """Asserts get_content_of_files reads the correct files"""

        content_1 = "a"
        content_2 = "b"

        with tempfile.TemporaryDirectory() as input_directory:

            # Set up test files
            with open(input_directory + "file1", "w") as handle:
                handle.write(content_1)

            with open(input_directory + "file2", "w") as handle:
                handle.write(content_2)

            expected_result = [content_1, content_2]

            actual_result = target_module.get_content_of_files(
                input_directory + "file1",
                input_directory + "file2"
            )

        self.assertEqual(expected_result, actual_result)

    def test_extend_zip(self):
        """Asserts that extend_zip works as intended"""

        with tempfile.TemporaryDirectory() as source_directory, \
            tempfile.TemporaryDirectory() as target_directory, \
            tempfile.TemporaryDirectory() as assertion_directory:

            directories_in_source = ["src/lambda", "tests"]

            for directory in directories_in_source:
                pathlib.Path(os.path.join(source_directory, directory)).mkdir(parents=True, exist_ok=True)

            pathlib.Path(os.path.join(source_directory, "initial")).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(source_directory, "initial", "test.txt"), "w") as handle:
                handle.write("test-content")

            with open(os.path.join(source_directory, "src", "lambda", "handler.py"), "w") as handle:
                handle.write("test-content")

            zip_path = os.path.join(target_directory, "target")
            shutil.make_archive(zip_path, "zip", os.path.join(source_directory, "initial"))

            # Verify the test setup was ok
            self.assertTrue(os.path.exists(zip_path + ".zip"))

            target_module.extend_zip(
                path_to_zip=zip_path + ".zip",
                code_directories=[
                    os.path.join(source_directory, "src"),
                    os.path.join(source_directory, "tests")
                ]
            )

            # Verify the zip still exists
            self.assertTrue(os.path.exists(zip_path + ".zip"))

            # Extract the zip
            shutil.unpack_archive(zip_path + ".zip", assertion_directory)

            # Assert that our code directories exist
            self.assertTrue(os.path.exists(os.path.join(assertion_directory, "src", "lambda", "handler.py")))
            self.assertTrue(os.path.exists(os.path.join(assertion_directory, "tests")))

            # Assert that the content of our initial zip is there as well
            self.assertTrue(os.path.exists(os.path.join(assertion_directory, "test.txt")))

    def test_get_build_dir(self):
        """Assert that get_build_dir works with the environment variable"""

        backup_env = os.environ.get(target_module.BUILD_DIR_ENV)

        os.environ[target_module.BUILD_DIR_ENV] = "test"

        self.assertEqual("test", target_module.get_build_dir())

        del os.environ[target_module.BUILD_DIR_ENV]

        with patch(self.module + "tempfile.gettempdir") as get_temp_mock:
            get_temp_mock.return_value = "test"

            self.assertEqual(os.path.join("test", "lambda_bundler_builds"), target_module.get_build_dir())

        if backup_env is not None:
            os.environ[target_module.BUILD_DIR_ENV] = backup_env

    def test_return_empty_if_skip_install(self):
        """Assert the decorator works as expected."""

        prev = os.environ.get("LAMBDA_BUNDLER_SKIP_INSTALL")

        os.environ["LAMBDA_BUNDLER_SKIP_INSTALL"] = "true"

        @target_module.return_empty_if_skip_install
        def inner():
            return "installed"

        with tempfile.TemporaryDirectory() as temp:

            os.environ[target_module.BUILD_DIR_ENV] = temp

            result = inner()
            self.assertTrue(result.endswith("empty.zip"))

            second_result = inner()
            self.assertTrue(second_result.endswith("empty.zip"))

            del os.environ["LAMBDA_BUNDLER_SKIP_INSTALL"]
            self.assertEqual("installed", inner())

        if prev is not None:
            os.environ["LAMBDA_BUNDLER_SKIP_INSTALL"] = prev

if __name__ == "__main__":
    unittest.main()
