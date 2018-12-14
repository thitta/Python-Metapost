import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metapost",
    version="0.0.3",
    author="Hsufeng Lee",
    author_email="thittalee@gmail.com",
    description="Tools for interpreting MetaPost",
    license='MIT License',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thitta/Python-MetaPost",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
