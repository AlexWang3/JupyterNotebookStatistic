import requests
import json
import os
from statistics import mean

contents_api_url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
github_token = ''
headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

def count_ipynb_files(owner, repo, path=""):
    response = requests.get(contents_api_url.format(owner=owner, repo=repo, path=path), headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch contents for {owner}/{repo} at {path}: {response.status_code}")
        return 0
    
    contents = response.json()
    count = 0

    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.ipynb'):
            count += 1
        elif item['type'] == 'dir':
            count += count_ipynb_files(owner, repo, item['path'])

    return count

with open('top_1000_python_repos.json', 'r') as f:
    repos = json.load(f)[:100]

ipynb_counts = []

for repo in repos:
    owner = repo['owner']['login']
    repo_name = repo['name']
    count = count_ipynb_files(owner, repo_name)
    print(count)
    ipynb_counts.append(count)

if ipynb_counts:
    max_ipynb = max(ipynb_counts)
    min_ipynb = min(ipynb_counts)
    avg_ipynb = mean(ipynb_counts)
    print(f"Maximum .ipynb files: {max_ipynb}")
    print(f"Minimum .ipynb files: {min_ipynb}")
    print(f"Average .ipynb files: {avg_ipynb:.2f}")