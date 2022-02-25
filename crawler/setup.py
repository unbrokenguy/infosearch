from setuptools import setup, find_packages
from io import open

import pathlib

BASE_DIR = pathlib.Path(__file__).parent

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name="Crawler",
    description="Crawl web pages easily",
    long_description="",
    long_description_content_type="text/markdown",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False,
    python_requires=">=3",
    entry_points={
        'console_scripts':
            'crawler = crawler.__main__:main'
    },
    author="Khaziev Bulat 11-806",
    keyword="",
    license="MIT",
    url="",
    download_url="",
    author_email="khazievbulatphanzilovich@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
