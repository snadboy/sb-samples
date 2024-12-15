from setuptools import setup, find_packages

setup(
    name="sb-samples",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sb-notion>=0.6.0",
        "python-dotenv>=0.19.0",
    ],
    author="snadboy",
    description="Sample projects using SB libraries",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/snadboy/sb-samples",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
