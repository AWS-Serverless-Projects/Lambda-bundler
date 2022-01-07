"""
Tests for the lambda_bundler.bundler module.
"""
import unittest
from unittest.mock import patch, ANY

import lambda_bundler.bundler as target_module

class TestBundler(unittest.TestCase):
    """
    Test Cases for the python dependencies.
    """

    def setUp(self):
        self.module = "lambda_bundler.bundler."

    def test_build_layer_package(self):
        """Asserts build_layer_package orchestrates the functions as expected."""

        with patch(self.module + "dependencies.collect_and_merge_requirements") as collect_mock, \
            patch(self.module + "dependencies.create_or_return_zipped_dependencies") as zip_mock:

            zip_mock.return_value = "some/path.zip"

            result = target_module.build_layer_package(
                ["abc"]
            )

            collect_mock.assert_called_with("abc")

            zip_mock.assert_called_with(
                requirements_information=ANY,
                output_directory_path=ANY,
                prefix_in_zip="python"
            )

            self.assertEqual("some/path.zip", result)

    def test_build_lambda_package(self):
        """Assert this function calls the right subroutines"""

        with patch(self.module + "dependencies.build_lambda_package_without_dependencies") as wo_mock:

            wo_mock.return_value = "without_dependencies.zip"

            return_value = target_module.build_lambda_package(
                code_directories=["abc"],
                exclude_patterns=["def"]
            )

            wo_mock.assert_called_once_with(
                code_directories=["abc"],
                exclude_patterns=["def"]
            )

            self.assertEqual("without_dependencies.zip", return_value)

        with patch(self.module + "dependencies.build_lambda_package_with_dependencies") as w_mock:

            w_mock.return_value = "with_dependencies.zip"

            result = target_module.build_lambda_package(
                code_directories=["abc"],
                requirement_files=["ghi"],
                exclude_patterns=["def"]
            )

            w_mock.assert_called_once_with(
                code_directories=["abc"],
                requirement_files=["ghi"],
                exclude_patterns=["def"]
            )

            self.assertEqual("with_dependencies.zip", result)

if __name__ == "__main__":
    unittest.main()
