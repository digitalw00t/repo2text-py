#!/usr/bin/env python3
import os
import subprocess
import argparse
from bs4 import BeautifulSoup

def clone_repo(repo_url):
    result = None
    repo_name = repo_url.split("/")[-1]
    if os.path.exists(repo_name):
        print("Repo already exists, pulling latest changes...")
        os.chdir(repo_name)
        repo_path = os.getcwd()
    else:
        print("Cloning repo...")
        result = subprocess.run(["git", "clone", "--depth=1", repo_url])
        repo_path = repo_name
    if result and result.returncode != 0:
        print("Error cloning repo")
        exit()
    print("Repo path:", repo_path)
    return repo_path

def get_file_contents(repo_path, file):
    result = subprocess.run(["git", "show", f"HEAD:{file}"], capture_output=True, cwd=repo_path)
    try:
        content = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        content = "Binary content"
    return content

def walk_dir(repo_path, types=None):
    print("Getting file listing...")
    result = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--name-only"],capture_output=True,cwd=repo_path,)
    files = result.stdout.decode().split("\n")
    print(f"Found {len(files)} files")

    file_data = []
    for file in files:
        if file:
            # Check file extension
            ext = os.path.splitext(file)[1][1:]
            if types and ext not in types:
                continue
            print(f"Getting contents of {file}")
            result = subprocess.run(["git", "show", f"HEAD:{file}"], capture_output=True, cwd=repo_path)
            content = result.stdout
            try:
                content = content.decode("utf-8")
            except UnicodeDecodeError:
                if isinstance(content, bytes):
                    content = "Binary content"
            file_data.append(f"\\n'''--- {file} ---\\n{content}\\n'''\\n")
    return file_data

def scrape_doc(doc_url):
  response = requests.get(doc_url)
  soup = BeautifulSoup(response.content, 'html.parser')
  return soup.get_text(separator="\n")

def write_text_file(repo_name, file_data, doc_text=None):
    filename = f"{repo_name}.txt"
    with open(filename, "w") as f:
        if doc_text:
            f.write(f"Documentation: {doc_url}\\n\\n{doc_text}\\n\\n")
        f.write(f"*GitHub Repository {repo_name}*\\n")
        for data in file_data:
            f.write(data)
    print(f"Text file saved: {filename}")

def get_local_file_contents(file_path):
    if os.path.isdir(file_path):
        contents = []
        for root, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                        contents.append(f"\\\\n\'\'\'--- {full_path} ---\\\\n{content}\\\\n\'\'\'\\\\n")
                    except UnicodeDecodeError:
                        print(f"Unable to read file {full_path} in utf-8 encoding.")
        return contents
    elif os.path.isfile(file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return [f"\\\\n\'\'\'--- {file_path} ---\\\\n{content}\\\\n\'\'\'\\\\n"]
        except UnicodeDecodeError:
            print(f"Unable to read file {file_path} in utf-8 encoding.")
            return []
    else:
        print(f"Path {file_path} does not exist.")
        return None


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
        help="Files to include in the output",
    )
    args = parser.parse_args()
    
    file_data = []
    
    if args.repo:
        repo_name = clone_repo(args.repo)
        file_data.extend(walk_dir(repo_name, args.types))
    else:
        repo_name = os.path.basename(os.getcwd())
    
    for file_path in args.files:
        content = get_local_file_contents(file_path)
        if content is not None:
            file_data.extend(content)

    doc_text = ""
    if args.doc:
        doc_text = scrape_doc(args.doc)

    write_text_file(repo_name, file_data, doc_text)

