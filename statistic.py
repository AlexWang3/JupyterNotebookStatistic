import requests
import time
import json
import stat, os, shutil
import subprocess
from retry import retry
from git import rmtree
from pathlib import Path
from statistics import mean

contents_api_url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
github_token = ''
headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Function to count .ipynb files in a repository
def count_ipynb_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += sum(1 for file in files if file.endswith('.ipynb'))
    return count

# Function to clone a repository
def clone_repository(repo_url, clone_dir):
    result = subprocess.run(['git', 'clone', repo_url, clone_dir], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to clone repository {repo_url}: {result.stderr}")
        return False
    return True

def readonly_to_writable(foo, file, err):
    if Path(file).suffix in ['.idx', '.pack'] and 'PermissionError' == err[0].__name__:
        os.chmod(file, stat.S_IWRITE)
        foo(file)

@retry(tries=15, delay=2)
def retry_rmtree(directory):
    rmtree(directory)

if not os.path.exists('clones'):
    os.makedirs('clones')

with open('top_1000_python_repos.json', 'r') as f:
    repos = json.load(f)[:1000]

ipynb_counts = []
for repo in repos:
    owner = repo['owner']['login']
    repo_name = repo['name']
    repo_url = repo['clone_url']
    clone_dir = os.path.join('clones', f"{owner}_{repo_name}")
    # Clone the repository
    if clone_repository(repo_url, clone_dir):
        # Count .ipynb files
        count = count_ipynb_files(clone_dir)
        ipynb_counts.append(count)
        print(count)
        # shutil.rmtree(clone_dir, onerror=readonly_to_writable)
        try:
            retry_rmtree(clone_dir)
        except Exception as e:
            print(f"Failed to delete repository {clone_dir} after retries: {e}")

if ipynb_counts:
    max_ipynb = max(ipynb_counts)
    min_ipynb = min(ipynb_counts)
    avg_ipynb = mean(ipynb_counts)
    print(f"Maximum .ipynb files: {max_ipynb}")
    print(f"Minimum .ipynb files: {min_ipynb}")
    print(f"Average .ipynb files: {avg_ipynb:.2f}")

with open('ipynb_counts_1000.txt', 'w') as f:
    for c in ipynb_counts:
        f.write(f"{c}\n")