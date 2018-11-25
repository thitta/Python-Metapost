import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metapost",
    version="0.0.1",
    author="Hsufeng Lee",
    author_email="thittalee@gmail.com",
    description="Tools for interpreting MetaPost",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thitta/Python-MetaPost",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
)