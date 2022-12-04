from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open("censuscoding/VERSION") as f:
    version = f.read().strip()

setup(
    name="censuscoding",
    author="Mark Howison",
    author_email="mhowison@ripl.org",
    version=version,
    url="https://github.com/ripl-org/censuscoding",
    description="Censuscoding, a privacy-preserving alternative to geocoding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Free for non-commercial use",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering"
    ],
    provides=["censuscoding"],
    install_requires=[
        "usaddress"
    ],
    packages=find_packages(),
    package_data={"censuscoding": ["VERSION", "data/*"]},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "censuscoding = censuscoding.__main__:main"
        ]
    }
)
