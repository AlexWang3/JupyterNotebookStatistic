import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from statistics import mean
from tqdm import tqdm

commits = []

commits_num = []          # across all repos
change_file_num = []      # across all commits
edit_line_num = []        # across all changed files  
add_delete_line_num = []  # across all changed files


def plot_and_save_distribution(data, filename, title = 'Distribution Plot',
                                xlabel = 'Value', ylabel = 'Frequency',
                                x_min = 0, x_max = 100, bin_width = 10):
    plt.clf()
    
    data_max = max(data)
    data_min = min(data)
    data_avg = mean(data)

    bins = np.arange(x_min, x_max + 1, bin_width)  # Bins for the specified range
    bins = np.concatenate(([-np.inf], bins, [np.inf]))  # Adding bins for values out of the range

    # Create the distribution plot
    sns.histplot(data, bins=bins, kde=True)

    # Add title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.figtext(0.15, 0.8, f'Min: {data_min}', fontsize=12, ha='left')
    plt.figtext(0.15, 0.75, f'Max: {data_max}', fontsize=12, ha='left')
    plt.figtext(0.15, 0.7, f'Average: {data_avg:.2f}', fontsize=12, ha='left')

    # Save the plot as an image
    plt.savefig(filename, format='png')


def get_line_change_num(diff):
    lines = diff.splitlines()
    minus_count = 0
    plus_count = 0
    edit_count = 0
    p_minus = False
    for l in lines:
        if l.startswith('+++') or l.startswith('---'):
            continue
        if l.startswith('-'):
            minus_count += 1
            p_minus = True
        elif l.startswith('+'):
            plus_count += 1
            if p_minus:
                edit_count += 1
            p_minus = False
        else:
            p_minus = False
    add_count = plus_count - minus_count
    return edit_count, add_count

if not os.path.exists('commits_summary'):
    os.makedirs('commits_summary')

with open('commits.json') as file:
    commits = json.load(file)

cur_repo_name = ''
cur_commit_hash = ''
commits_num.append(0)

for item in tqdm(commits):
    if item['repo'] != cur_repo_name:
        cur_repo_name = item['repo']
        cur_commit_hash = ''
        commits_num.append(0)
    if item['commit'] != cur_commit_hash:
        cur_commit_hash = item['commit']
        commits_num[-1] += 1
        change_file_num.append(1)
    else:
        change_file_num[-1] += 1

    edit, add = get_line_change_num(item['diff'])
    edit_line_num.append(edit)
    add_delete_line_num.append(add)

plot_and_save_distribution(commits_num, 'commits_summary/commits_num.png', title='Number of commits for each repo', 
                           xlabel='Number of commits', ylabel='Frequence',
                           x_min = 0, x_max = 100, bin_width=10)
plot_and_save_distribution(change_file_num, 'commits_summary/change_file_num.png', title='Number of file changed for each commit',
                        xlabel='Number of file changed', ylabel='Frequence',
                        x_min = 0, x_max = 100, bin_width=10)
plot_and_save_distribution(edit_line_num, 'commits_summary/edit_line_num.png', title='Number of line edited for each file changed', 
                           xlabel='Number of line edited', ylabel='Frequence',
                           x_min = 0, x_max = 100, bin_width=10)
plot_and_save_distribution(add_delete_line_num, 'commits_summary/add_delete_line_num.png', title='Number of line added/deleted for each file changed', 
                           xlabel='Number of line added/deleted', ylabel='Frequence',
                           x_min = -100, x_max = 100, bin_width=10)

    
