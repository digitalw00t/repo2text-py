#!/usr/bin/env python3

import subprocess
import os
import argparse
from bs4 import BeautifulSoup 
import requests

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
    content = result.stdout.decode('utf-8')
  except UnicodeDecodeError:
    content = "Binary content"

  return content

def walk_dir(repo_path):
  print("Getting file listing...")
  result = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--name-only"], capture_output=True, cwd=repo_path)
  files = result.stdout.decode().split("\n")
  print(f"Found {len(files)} files")

  file_data = []
  for file in files:
    if file:
      print(f"Getting contents of {file}")
      result = subprocess.run(["git", "show", f"HEAD:{file}"], capture_output=True, cwd=repo_path)
      content = result.stdout
      try:
        content = content.decode('utf-8')
      except UnicodeDecodeError:
        if isinstance(content, bytes):
          content = "Binary content"
      file_data.append(f"\n'''--- {file} ---\n{content}\n'''\n")
  return file_data

def scrape_doc(doc_url):
  response = requests.get(doc_url)
  soup = BeautifulSoup(response.content, 'html.parser')
  return soup.get_text(separator="\n")

def write_text_file(repo_name, file_data, doc_text):
  filename = f"{repo_name}.txt"
  with open(filename, 'w') as f:
    if doc_text:
      f.write(f"Documentation: {doc_url}\n\n{doc_text}\n\n")
    f.write(f"*GitHub Repository {repo_name}*\n")
    for data in file_data:
      f.write(data)
  print(f"Text file saved: {filename}")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-r", "--repo", required=True, help="GitHub repo URL")
  parser.add_argument("-d", "--doc", required=False, help="Documentation URL")
  
  args = parser.parse_args()
  repo_name = clone_repo(args.repo)
  file_data = walk_dir(repo_name)

  doc_text = ""
  if args.doc:
    doc_text = scrape_doc(args.doc)

  write_text_file(repo_name, file_data, doc_text)
