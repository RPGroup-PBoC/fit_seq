import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fit_seq",
    version="0.0.1",
    author="Manuel Razo, Emmanuel Flores, Rob Phillips",
    author_email="mrazomej {at} caltech {dot} edu",
    description="This repository contains all active research materials for the fit_esq project that combines sort-seq data and population genetics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrazomej/fit_seq.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
