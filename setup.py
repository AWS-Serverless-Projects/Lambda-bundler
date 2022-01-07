"""Packaging configuration"""
import json
import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "0.1.0"

ENV_GITHUB_EVENT_PATH = "GITHUB_EVENT_PATH"

def _load_event() -> dict:
    with open(os.environ[ENV_GITHUB_EVENT_PATH]) as event_handle:
        return json.load(event_handle)

def get_release_from_pipeline():
    """
    If the build has been triggered by a release event in a github pipeline,
    we take the version number from the release event. If not we return the
    version constant.
    """

    try:

        event = _load_event()

        release_name: str = event["release"]["tag_name"]
        # Strip the leading v if it exists
        version_number = release_name[1:] if release_name.startswith("v") else release_name
        print(f"Setting the version number to {version_number} from the Github Pipeline")

        return version_number
    except KeyError:
        # We'll get a key error if the Environment variable
        # isn't set or the release key is not in the event
        # In both cases, we want to stay with the regular
        # version number from this file
        return VERSION

VERSION = get_release_from_pipeline()

setuptools.setup(
    name="lambda-bundler",
    version=VERSION,
    author="Maurice Borgmeier",
    description="A utility to bundle python code and/or dependencies for deployment to AWS Lambda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MauriceBrg/lambda_bundler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    extras_require={
        "dev": [
            "pylint==2.5.3",
            "pytest==5.4.3",
            "pytest-cov==2.10.0",
            "setuptools==40.8",
            "twine==3.2.0",
            "wheel==0.34.2"
        ]
    }
)
