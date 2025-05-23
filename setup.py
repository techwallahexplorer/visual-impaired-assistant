from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="visual-impaired-assistant",
    version="1.1.0",
    author="Your Name",
    author_email="user@example.com",
    description="A multilingual speech recognition and analysis assistant for visually impaired users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/techwallahexplorer/visual-impaired-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
        "Natural Language :: Hindi",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "visual-assistant=visually:main",
        ],
    },
)
