# repo2text.py

## Introduction

`repo2text.py` is a Python script that converts Git repositories into text files, allowing you to explore and interact with code repositories in a single text document.

## Features

- Clones Git repositories.
- Walks through directories to fetch file contents.
- Writes delimited file contents to a text file.
- Supports filtering specific file extensions.
- Respects `.gitignore` file rules for both current directory and specified repository path cases.
- Allows specifying file extensions to ignore via command-line arguments.
- Always ignores specific hard-coded file extensions (`.log`, `.exe`).

## Usage

### Installation

Before using `repo2text.py`, make sure you have Python 3.6+ installed and install the required `gitpython` module using `pip`:

```bash
pip install gitpython
Basic Usage
Clone a Git repository, retrieve file contents, and save them in a text file:

python repo2text.py --repo <GIT_REPO_URL>
Advanced Usage
Filter specific file extensions and clone private repositories:

python repo2text.py --repo <GIT_REPO_URL> --types py html md json
Handling Local Repositories
Convert the current directory or a specified local repository path into a text file:

For the current directory:

python repo2text.py .
For a specified repository path:

python repo2text.py <REPO_PATH>
Ignoring Specific File Extensions
You can specify additional file extensions to ignore:

python repo2text.py <REPO_PATH> --ignore-extensions .log .tmp
Checking Version
To check the script's version, use:

python repo2text.py --version
Examples
Provide a variety of examples showcasing different use cases, including public and private repositories.
Include example output files for better understanding.
Limitations
Explain why large binary files are omitted.
Suggest solutions or workarounds for dealing with large repositories.
License
repo2text.py is distributed under the MIT License. Feel free to use and modify the script as needed.

Contributing
We welcome contributions! If you'd like to improve this script, please submit pull requests or open issues on the GitHub repository.

Credits
This project is based on RepoToText. Special thanks to the original creator for the inspiration.
