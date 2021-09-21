from setuptools import setup, find_packages


version = {}
with open("local_judge/version.py") as fp:
    exec(fp.read(), version)


from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="local-judge",
    version=version["__version__"],
    description="Given source code, Makefile (or build commands), input files, and answer files then judge the program locally.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Huang Po-Hsuan",
    author_email="aben20807@gmail.com",
    url="https://github.com/aben20807/local-judge",
    packages=find_packages(include=["local_judge"]),
    license_files=("LICENSE"),
    entry_points={
        "console_scripts": [
            "judge=local_judge.judge:main",
            "ta_judge=local_judge.ta_judge:main",
        ],
    },
    python_requires=">=3.6.0",
    extras_require={
        "ta": ["openpyxl>=2.5.0", "rarfile>=4.0"],
    },
)
