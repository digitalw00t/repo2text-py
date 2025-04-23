"""
Command-line interface for repo2text.
"""

import argparse
import os
from . import __version__
from . import core

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Convert GitHub repositories and documentation to text files")
    parser.add_argument("-r", "--repo", required=False, help="GitHub repo URL")
    parser.add_argument("-d", "--doc", required=False, help="Documentation URL")
    parser.add_argument(
        "-t",
        "--token",
        action="store_true",
        help="Include token count in file headers",
    )
    parser.add_argument(
        "-i",
        "--ignore-extensions",
        required=False,
        nargs="+",
        help="File extensions to ignore, e.g., .log, .tmp",
    )
    parser.add_argument(
        "files",
        metavar="F",
        type=str,
        nargs="*",
        default=["."],
        help="Files or directories to include in the output (use '.' for the current directory)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()
    
    file_data = []
    doc_text = None
    
    if args.repo:
        repo_path = core.clone_repo(args.repo)
        gitignore_patterns = core.get_gitignore_patterns(repo_path)
    else:
        repo_path = os.path.abspath(args.files[0])
        gitignore_patterns = core.get_gitignore_patterns(repo_path)
    
    if args.doc:
        doc_text = core.scrape_doc(args.doc)
    
    file_data = core.get_local_file_contents(
        repo_path,
        gitignore_patterns,
        args.ignore_extensions or [],
        args.token
    )
    
    repo_name = os.path.basename(repo_path)
    core.write_text_file(repo_name, file_data, doc_text)

if __name__ == "__main__":
    main() 