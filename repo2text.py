#!/usr/bin/env python3
import os
import subprocess
import argparse
import requests
from bs4 import BeautifulSoup
import sys
import fnmatch

__VERSION__ = "v1.1.0"

def get_gitignore_patterns(repo_path):
    gitignore_path = os.path.join(repo_path, '.gitignore')
    patterns = []
    print(f"Checking for .gitignore file at: {gitignore_path}")  # Debugging statement
    if os.path.exists(gitignore_path):
        print(f".gitignore file found: {gitignore_path}")  # Debugging statement
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    else:
        print(f".gitignore file not found: {gitignore_path}")  # Debugging statement
    print(f"Gitignore patterns: {patterns}")  # Debugging statement
    return patterns

def is_ignored(file_path, gitignore_patterns):
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            print(f"File {file_path} is ignored due to pattern {pattern}")  # Debugging statement
            return True
    return False

def get_local_file_contents(file_path, gitignore_patterns):
    contents = []
    ignore_dirs = ['.git', '__pycache__']  # List of directories to ignore
    ignore_file_types = {
        "ELF 64-bit LSB pie executable": None,
        "symbolic link to": None
    }  # Dictionary of file types to ignore

    print(f"Processing file path: {file_path}")  # Debugging statement

    if file_path == '.':  # If the path is the current directory
        file_path = os.getcwd()  # Get the absolute path of the current directory
        print(f"Current directory: {file_path}")  # Debugging statement

    if os.path.isdir(file_path):  # If the path is a directory
        print(f"Directory: {file_path}")  # Debugging statement
        for root, dirs, files in os.walk(file_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]  # ignore directories in ignore_dirs
            relative_path = os.path.relpath(root, file_path)
            if is_ignored(relative_path, gitignore_patterns):
                print(f"Ignoring directory: {relative_path}")
                continue
            for file in files:
                full_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(full_path, file_path)  # Get the relative path of the file
                if is_ignored(relative_file_path, gitignore_patterns):
                    print(f"Ignoring file: {relative_file_path}")
                    continue
                if not any(ignore_dir in full_path for ignore_dir in ignore_dirs):  # ignore files in ignored directories
                    file_type = subprocess.run(['file', '-b', full_path], capture_output=True, text=True).stdout.strip()
                    if any(file_type.startswith(ignore_file_type) for ignore_file_type in ignore_file_types):
                        print(f"Skipping file {full_path} of type {file_type}", file=sys.stderr)
                        continue
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                        contents.append(f"\n'''###--- {relative_file_path} ---###\n{content}\n'''\n")
                        print(f"Processed file: {relative_file_path}")  # Debugging statement
                    except UnicodeDecodeError:
                        print(f"Unable to read file {full_path} in utf-8 encoding.")
    elif os.path.isfile(file_path):  # If the path is a file
        print(f"File: {file_path}")  # Debugging statement
        relative_path = os.path.relpath(file_path, os.getcwd())  # Get the relative path of the file
        if not is_ignored(relative_path, gitignore_patterns):  # Check if the file should be ignored
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                contents.append(f"\n'''###--- {relative_path} ---###\n{content}\n'''\n")
                print(f"Processed file: {relative_path}")  # Debugging statement
            except UnicodeDecodeError:
                print(f"Unable to read file {file_path} in utf-8 encoding.")
    else:  # If the path is neither a file nor a directory
        print(f"Path {file_path} does not exist.")  # Debugging statement

    return contents

def clone_repo(repo_url):
    result = None
    repo_name = repo_url.split("/")[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]  # Correctly remove '.git' from the repo name
    if os.path.exists(repo_name):
        print("Repo already exists, pulling latest changes...")
        os.chdir(repo_name)
        repo_path = os.getcwd()
    else:
        print("Cloning repo...")
        result = subprocess.run(["git", "clone", "--depth=1", repo_url], check=True)
        # Ensure we change to the cloned repo's directory
        os.chdir(repo_name)
        repo_path = os.getcwd()
    print("Repo path:", repo_path)
    return repo_path

def scrape_doc(doc_url):
    response = requests.get(doc_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text(separator="\n")

def write_text_file(repo_name, file_data, doc_text=None, split=None):
    file_index = 1
    current_char_count = 0
    content_buffer = ""

    if doc_text:
        content_buffer += f"Documentation: {doc_url}\n\n{doc_text}\n\n"

    content_buffer += f"*GitHub Repository {repo_name}*\n"
    filename = f"{repo_name}.txt"

    for data in file_data:
        if split and (current_char_count + len(data) > split):
            with open(filename, "w") as f:
                f.write(content_buffer)
            print(f"Text file saved: {filename}")

            file_index += 1
            filename = f"{repo_name}_part{file_index}.txt"
            content_buffer = f"*GitHub Repository {repo_name}*\n"
            current_char_count = 0  # Reset character count for the new file

        content_buffer += data
        current_char_count += len(data)

    with open(filename, "w") as f:
        f.write(content_buffer)
    print(f"Text file saved: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo", required=False, help="GitHub repo URL")
    parser.add_argument("-d", "--doc", required=False, help="Documentation URL")
    parser.add_argument(
        "-t",
        "--types",
        required=False,
        nargs="+",
        help="File extensions to include (without dot), e.g., py, md, html, json",
    )
    parser.add_argument(
        "files",
        metavar="F",
        type=str,
        nargs="*",
        help="Files or directories to include in the output (use '.' for the current directory)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__VERSION__}")
    args = parser.parse_args()
    
    file_data = []
    
    if args.repo:
        repo_name = clone_repo(args.repo)
        gitignore_patterns = get_gitignore_patterns(repo_name)
    else:
        repo_path = os.path.abspath(args.files[0])
        repo_name = os.path.basename(repo_path)
        gitignore_patterns = get_gitignore_patterns(repo_path)
    
    errors = []
    for file_path in args.files:
        print(f"Processing file path: {file_path}")  # Debugging statement
        content = get_local_file_contents(file_path, gitignore_patterns)
        if content:
            file_data.extend(content)
        else:
            print(f"No content found for file path: {file_path}")  # Debugging statement
            errors.append(f"Error processing {file_path}")

    doc_text = ""
    if args.doc:
        doc_text = scrape_doc(args.doc)

    write_text_file(repo_name, file_data, doc_text)

    if errors:
        print("Errors occurred while processing the following files or directories:")
        for error in errors:
            print(error)

