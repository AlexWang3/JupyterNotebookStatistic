import requests
import time
import json
import stat, os, shutil
import subprocess
import nbformat
import difflib
from retry import retry
from git import rmtree
from pathlib import Path
from statistics import mean
from tqdm import tqdm



git_log_command = ['git', 'log', '--name-only', '--pretty=format:%H%n%s']
git_diff_command = 'git diff {}^1 -- {}'
repo_number = 100

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

def concatenate_code_cells(notebook_content):
    try:
        notebook = nbformat.reads(notebook_content, as_version=4)
    except nbformat.reader.NotJSONError:
        return ""
    # Initialize a list to store code cells
    code_cells = []

    # Iterate through the cells in the notebook
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            code_cells.append(cell.source)
    
    # Concatenate all code cells into a single string
    concatenated_code = "\n".join(code_cells)
    return concatenated_code

def output_string_difference(string1, string2):
    # Use difflib to find differences
    diff = difflib.unified_diff(string1.splitlines(), string2.splitlines())
    # Convert the generator to a list
    diff_list = list(diff)
    
    # Join the list into a single string with newline characters
    diff_output = '\n'.join(diff_list)
    
    return diff_output


@retry(tries=15, delay=2)
def retry_rmtree(directory):
    file_path = u"\\\\?\\" + os.path.join(os.getcwd(), directory)
    rmtree(file_path)


if not os.path.exists('clones'):
    os.makedirs('clones')

with open('top_1000_python_repos.json', 'r') as f:
    repos = json.load(f)[:repo_number]

ipynb_counts = []
all_commits = []
for repo in tqdm(repos):
    owner = repo['owner']['login']
    repo_name = repo['name']
    repo_url = repo['clone_url']
    clone_dir = os.path.join('clones', f"{owner}_{repo_name}")
    # Clone the repository
    if clone_repository(repo_url, clone_dir):
        git_log_output = subprocess.run(['git', 'log', '--name-only', '--pretty=format:%n%H%n%s']
                                    ,cwd=clone_dir, stdout=subprocess.PIPE, text=True).stdout
        commits = []
        current_commit = None
        process_flag = 0
        # # Process the log output
        for line in git_log_output.splitlines():
            if not line.strip():
                # empth line
                if current_commit:
                    commits.append(current_commit)
                process_flag = 0
                continue
            if process_flag == 0:
                # hash
                # print("hash: " + line)
                current_commit = {'commit': line, 'files': [], 'messages': []}
                process_flag = 1
            elif process_flag == 1:
                # Commit message
                # print("message: " + line)
                current_commit['messages'].append(line)
                process_flag = 2
            else:
                # File name
                #print("file: " + line)
                file_name = line.strip()
                if not file_name.endswith('.ipynb'):
                    continue
                file_path = os.path.join(clone_dir, file_name)
                #print(file_path)
                cur_commit = current_commit["commit"]
                pre_commit = cur_commit + '^'
                #cur_code = concatenate_code_cells(file_path)
                cur_content = subprocess.run(['git', 'show', f'{cur_commit}:{file_name}'], cwd=clone_dir,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
                pre_content = subprocess.run(['git', 'show', f'{pre_commit}:{file_name}'], cwd=clone_dir,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
                cur_code = concatenate_code_cells(cur_content)
                pre_code = concatenate_code_cells(pre_content)
                
                diff_output = output_string_difference(pre_code, cur_code)
                current_commit['files'].append({'file': file_name, 'diff': diff_output})
                
        if current_commit:
            commits.append(current_commit)

        # Append repo details to the main list
        for commit in commits:
            for file in commit['files']:
                all_commits.append({
                    "repo": repo_name,
                    "commit": commit['commit'],
                    "file": file['file'],
                    "message": " ".join(commit['messages']),
                    "diff": file['diff']
                })

        try:
            retry_rmtree(clone_dir)
        except Exception as e:
            print(f"Failed to delete repository {clone_dir} after retries: {e}")

# Output to JSON 
with open('commits.json', 'w') as f:
    json.dump(all_commits, f, indent=2)