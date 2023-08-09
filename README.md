```markdown
# repo2text.py

## About

repo2text.py is a Python script to convert a Git repository into a text file containing the repository's file contents.

It recursively clones the repository, walks the directory tree, gets the contents of each file, and writes the files with delimiters into an output text file. This allows exploring and interacting with an entire code repository in a single text file. 

The script utilizes the gitpython module to handle cloning and interacting with Git repositories.

## Usage

```
python repo2text.py --repo <GIT_REPO_URL>  
```

This will:

- Clone the repository to a local folder
- Walk the directory tree and fetch file contents 
- Write the delimited file contents to a `.txt` file

The output text file will be saved in the current working directory.

By default, all file types are included. To only include specific file extensions, use:

```
python repo2text.py --repo <URL> --types py html md json
```

To check the version of the script, use:

```
python repo2text.py --version
```

This will print the version information and exit.

## Installation

repo2text.py requires:

- Python 3.6+
- gitpython (`pip install gitpython`)

## Example 

Input:

```
python repo2text.py --repo https://github.com/user/repo
```

Output: myrepo.txt

```
'''--- README.md ---
# My Repo 
This is the README
'''

'''--- src/main.py ---  
print("Hello World!")
''' 
```

This outputs a text file `myrepo.txt` containing the contents of files in the repository.

## Caveats

- Large binary files are omitted from the output  
- Output file size can be large depending on repo size
- Only public repos are accessible currently

## License

MIT License - feel free to use and modify the script as needed.

## Credit

This project was created from the https://github.com/JeremiahPetersen/RepoToText.  Since I had issues getting react to behave, and I really didn't want to fire up a browser to do this I made this project.  Pop by and give it some love please.
```
