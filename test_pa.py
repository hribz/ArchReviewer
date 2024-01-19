# -*- coding: UTF-8 -*-
import json
import git
import logging
import os
import shutil
import subprocess
import codecs
import requests

def clone_repository(repository_url, destination_folder, branch='master'):
    try:
        repo = git.Repo.clone_from(repository_url, destination_folder, branch=branch, single_branch=True)
    except git.exc.GitCommandError:
        logging.log(level=logging.ERROR, msg=("clone " + repository_url + " to " + destination_folder + " failed"  ))
        return None
    return repo

def is_folder_empty(folder_path):
    if not os.path.exists(folder_path):
        return True
    files = os.listdir(folder_path)
    return not files

_TEXT_BOMS = (
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF8,
    )

def is_binary_file(file):
    initial_bytes = file.data_stream.read(8192)
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b'\0' in initial_bytes

def binary_filter(commit, path):
    try:
        file = commit.tree[path]
        if is_binary_file(file):
            return None
        else:
            file_content = file.data_stream.read().decode('utf-8')
            return file_content
    except KeyError:
        print("File not found in commit")
        return None

ground_truth = []
with open('tools/ground_truth.json', 'r') as f:
    ground_truth = json.load(f)

current_directory = os.getcwd()
work_dir = os.path.join(current_directory, 'real-project')
repo_num = 0
commit_num = 0
file_num = 0
line_num = 0

for truth in ground_truth:
    repo_name = truth["repo_name"]
    repo_url = truth["url"]
    repo_branch = truth["branch"]
    # real-project/repo_name
    repo_dir = os.path.join(work_dir, repo_name)
    # real-project/repo_name/source
    repo_source = os.path.join(repo_dir, 'source')
    repo_new_commit = os.path.join(repo_source, 'new_commit')
    need_clone = True
    if not os.path.exists(repo_new_commit):
        os.makedirs(repo_new_commit)
    else:
        if not is_folder_empty(repo_new_commit):
            need_clone = False
    if need_clone:
        repo = clone_repository(repo_url, repo_new_commit, repo_branch)
        if repo is None:
            raise ConnectionError("clone repo failed")
    else:
        repo = git.Repo(repo_new_commit)
        if repo is None:
            raise ConnectionError("can't get repo")
    
    for commit_json in truth["commits"]:
        detail = commit_json["detail"]
        
        for file_name in detail.keys():
            file_num = file_num + 1
            line_num = line_num + len(detail[file_name]["arc_line"])

        commit_hash = commit_json["commit_hash"]
        try:
            commit = repo.commit(commit_hash)
        except ValueError as e:
            print("Commit with hash %s not found: %s" % (commit_hash, str(e)))
            continue

        file_list = {"status": 0, "msg": "", "payload": []}
        for parent in commit.parents:
            for change in parent.diff(commit):
                file_type = change.change_type
                file_path = change.b_path
                file_binary = False

                if file_type == "A":
                    file_content_new = binary_filter(commit, change.b_path)
                elif file_type == "D":
                    file_content_old = binary_filter(commit, change.a_path)
                else:
                    file_diff = repo.git.diff(parent, commit, change.a_path, change.b_path)
                    file_content_old = binary_filter(parent, change.a_path)
                    file_content_new = binary_filter(commit, change.b_path)
                if file_content_new is None:
                    file_binary = True
                file = {
                    "binary": file_binary,
                    "path": file_path,
                    "type": file_type,
                    "diff": file_diff,
                    "arch_line": None,
                    "content_old": file_content_old,
                    "content_new": file_content_new
                    }
                file_list["payload"].append(file)
        with codecs.open('file_list.json', 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2, ensure_ascii=False)
        params = [{"repo_id": "0","hash": commit_hash}]
        response = requests.post('http://localhost:12499/inference', data=params)
        data = {}
        try:
            data = response.json()
            print(data)
        except requests.exceptions.JSONDecodeError as e:
            print('Error decoding JSON: '+ str(e))
        
        with open(repo_dir+'/_ArchReviewer/result_for_backend.json', 'w') as f:
            json.dump(data, f, indent=2)

    # with open('test_real_project.txt', 'w') as f:
    #     f.write(repo_dir)

    # subprocess.call(['ArchReviewer', '--kind=archinfo', '--list=test_real_project.txt'])

    print(repo_name+' finish\n')
    repo_num = repo_num+1
    commit_num = commit_num+len(truth["commits"])
    
print("repo num: %d, commit num: %d, file num: %d, line num: %d" % (repo_num, commit_num, file_num, line_num))