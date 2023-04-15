import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezlite",
    version="0.2.7",
    author="t.ibi",
    author_email="t.ibi@estyle-inc.jp",
    description="For the razy who wants to write programs with ease.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Taichi-Ibi/ezlite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
