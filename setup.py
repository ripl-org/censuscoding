from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open("censuscoding/VERSION") as f:
    version = f.read().strip()

setup(
    name="censuscoding",
    author=["Mark Howison", "Daniel Molitor"],
    author_email=["mhowison@ripl.org", "dmolitor@ripl.org"],
    version=version,
    url="https://github.com/ripl-org/censuscoding",
    description="Censuscoding: determine the Census blockgroup for a street address",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Free for non-commercial use",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
    ],
    provides=["censuscoding"],
    install_requires=[
        "pandas",
        "usaddress"
    ],
    packages=find_packages(),
    package_data={"censuscoding": ["VERSION", "data"]},
    entry_points={
        "console_scripts": [
            "censuscoding = censuscoding.__main__:main"
        ]
    }
)
