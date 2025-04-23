"""
Core functionality for repo2text.
"""

import os
import fnmatch
import subprocess
import sys
import tiktoken
import requests
from bs4 import BeautifulSoup

IGNORED_EXTENSIONS = [
    '.lock',
    # Compiled executables and libraries
    '.exe', '.dll', '.so', '.a', '.lib', '.dylib', '.o', '.obj',
    # Compressed archives
    '.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.bz2', '.gz', '.xz', '.z', '.lz', '.lzma', '.lzo', '.rz', '.sz', '.dz',
    # Application-specific files
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    # Media files (less common)
    '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.wav', '.flac', '.ogg', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.m4a', '.aac',
    # Virtual machine and container images
    '.iso', '.vmdk', '.qcow2', '.vdi', '.vhd', '.vhdx', '.ova', '.ovf',
    # Database files
    '.db', '.sqlite', '.mdb', '.accdb', '.frm', '.ibd', '.dbf',
    # Java-related files
    '.jar', '.class', '.war', '.ear', '.jpi',
    # Python bytecode and packages
    '.pyc', '.pyo', '.pyd', '.egg', '.whl',
    # Other potentially important extensions
    '.deb', '.rpm', '.apk', '.msi', '.dmg', '.pkg', '.bin', '.dat', '.data',
    '.dump', '.img', '.toast', '.vcd', '.crx', '.xpi', '.lockb', 'package-lock.json', '.svg',
    '.eot', '.otf', '.ttf', '.woff', '.woff2',
    '.ico', '.icns', '.cur',
    '.cab', '.dmp', '.msp', '.msm',
    '.keystore', '.jks', '.truststore', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.csr',
    '.key', '.pub', '.sig', '.pgp', '.gpg',
    '.nupkg', '.snupkg', '.appx', '.msix', '.msp', '.msu',
    '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
    '.ko', '.sys', '.elf',
    '.swf', '.fla', '.swc',
    '.rlib', '.pdb', '.idb', '.pdb', '.dbg',
    '.sdf', '.bak', '.tmp', '.temp', '.log', '.tlog', '.ilk',
    '.bpl', '.dcu', '.dcp', '.dcpil', '.drc',
    '.aps', '.res', '.rsrc', '.rc', '.resx',
    '.prefs', '.properties', '.ini', '.cfg', '.config', '.conf',
    '.DS_Store', '.localized', '.svn', '.git', '.gitignore', '.gitkeep',
]

def get_gitignore_patterns(repo_path):
    """Get patterns from .gitignore file."""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line.replace(os.sep, '/'))
    return patterns

def is_ignored(file_path, gitignore_patterns):
    """Check if a file should be ignored based on gitignore patterns."""
    file_path = file_path.replace(os.sep, '/')
    
    for pattern in gitignore_patterns:
        pattern = pattern.replace(os.sep, '/')
        
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path, f"*/{pattern}"):
            return True
        
        if pattern.endswith('/') and file_path.startswith(pattern):
            return True
    
    return False

def count_tokens(content: str) -> int:
    """Count the number of tokens in a string using tiktoken."""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    return len(tokens)

def get_local_file_contents(file_path, gitignore_patterns, ignore_extensions, count_tokens_flag=False):
    """Get contents of local files with optional token counting."""
    contents = []
    ignore_dirs = ['.git', '__pycache__']
    ignore_file_types = {
        "ELF 64-bit LSB pie executable": None,
        "symbolic link to": None
    }
    all_ignored_extensions = set(IGNORED_EXTENSIONS + ignore_extensions)

    if file_path == '.':
        file_path = os.getcwd()

    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            relative_path = os.path.relpath(root, file_path)
            if is_ignored(relative_path, gitignore_patterns):
                continue
            for file in files:
                full_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(full_path, file_path)
                if is_ignored(relative_file_path, gitignore_patterns) or os.path.splitext(file)[1] in all_ignored_extensions:
                    continue
                if not any(ignore_dir in full_path for ignore_dir in ignore_dirs):
                    file_type = subprocess.run(['file', '-b', full_path], capture_output=True, text=True).stdout.strip()
                    if any(file_type.startswith(ignore_file_type) for ignore_file_type in ignore_file_types):
                        continue
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                        if count_tokens_flag:
                            token_count = count_tokens(content)
                            contents.append(f"\n'''###--- {relative_file_path} {token_count} tokens ---###\n{content}\n'''\n")
                        else:
                            contents.append(f"\n'''###--- {relative_file_path} ---###\n{content}\n'''\n")
                    except UnicodeDecodeError:
                        print(f"Unable to read file {full_path} in utf-8 encoding.", file=sys.stderr)
    elif os.path.isfile(file_path):
        relative_path = os.path.relpath(file_path, os.getcwd())
        if not is_ignored(relative_path, gitignore_patterns) and os.path.splitext(file_path)[1] not in all_ignored_extensions:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if count_tokens_flag:
                    token_count = count_tokens(content)
                    contents.append(f"\n'''###--- {relative_path} {token_count} tokens ---###\n{content}\n'''\n")
                else:
                    contents.append(f"\n'''###--- {relative_path} ---###\n{content}\n'''\n")
            except UnicodeDecodeError:
                print(f"Unable to read file {file_path} in utf-8 encoding.", file=sys.stderr)
    else:
        print(f"Path {file_path} does not exist.", file=sys.stderr)

    return contents

def clone_repo(repo_url):
    """Clone a git repository or update if it already exists."""
    repo_name = repo_url.split("/")[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    if os.path.exists(repo_name):
        print("Repo already exists, pulling latest changes...")
        os.chdir(repo_name)
        repo_path = os.getcwd()
    else:
        print("Cloning repo...")
        subprocess.run(["git", "clone", "--depth=1", repo_url], check=True)
        os.chdir(repo_name)
        repo_path = os.getcwd()
    return repo_path

def scrape_doc(doc_url):
    """Scrape documentation from a URL."""
    response = requests.get(doc_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text(separator="\n")

def write_text_file(repo_name, file_data, doc_text=None, split=None):
    """Write the collected data to text files."""
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
            current_char_count = 0

        content_buffer += data
        current_char_count += len(data)

    with open(filename, "w") as f:
        f.write(content_buffer)
    print(f"Text file saved: {filename}") 