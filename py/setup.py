from setuptools import setup, find_packages

setup(
    name="py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
