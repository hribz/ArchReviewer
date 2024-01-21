# -*- coding: UTF-8 -*-
import json
import logging
import os
import threading
import time
from typing import Optional, List
import re

from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv
import subprocess
import requests
import shutil

IP = "localhost"
PORT = "12499"

config = {
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": ""
}


class Inference(Flask):
    def __init__(self, *args, **kwargs):
        super(Inference, self).__init__(*args, **kwargs)


app = Inference(__name__)


@app.route("/inference", methods=["POST"])
def inference():
    """
    request format:
    POST /inference
    [
        {
            "repo_id": ...,
            "hash": ...
        },
        {
            "repo_id": ...,
            "hash": ...
        },
        ...
    ]
    return format:
    [
    {
        "result": "arm",
        "detail": {
            "file_path_new_1": {
                "arch_line": [
                    "line", "line1-line2", ...
                ],
                "comments": {
                    "line(changed)": "commit line",
                    "begin-end": "commit block"
                },
            },
            "file_path_new_2": {
                "arch_line": [
                    "line", "line1-line2", ...
                ],
                "comments": {
                    "line(changed)": "commit line",
                    "begin-end": "commit block"
                },
            },
        }
        ...
    },
    {
        "result": "",
        "detail": {}
    },
    ...
    ]
    """
    commits = []
    try:
        raw_data = request.get_data(as_text=True)
        commits = json.loads(raw_data)
        print("raw_data: "+raw_data)
        print(commits)
        if len(commits) == 0 or type(commits) != list:
            raise Exception()
        for commit in commits:
            if type(commit) != dict:
                raise Exception()
    except:
        abort(400)

    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, 'git_repo.txt')
    git_repo_path = os.path.join(current_directory, 'git-repo')
    with open(file_path, 'w') as file:
        file.write(git_repo_path)
    source_floder = os.path.join(git_repo_path, 'source')
    if not os.path.exists(source_floder):
        os.makedirs(source_floder)
    else:
        shutil.rmtree(source_floder)
    old_commit_floder = os.path.join(source_floder, 'old_commit')
    new_commit_floder = os.path.join(source_floder, 'new_commit')
    os.makedirs(old_commit_floder)
    os.makedirs(new_commit_floder)
    result_json = []
    result_file_path = 'git-repo/_ArchReviewer/result_for_backend.json'

    for commit in commits:
        params = {'repo_id': commit.get('repo_id'), 'commit_hash': commit.get('hash')}
        # response = requests.get('http://47.94.210.196:12888/api/file', params=params)
        # json_data = response.json()
        with open('file_list.json', 'r') as f:
            json_data = json.load(f)
        # check request status
        # if response.status_code != 200:
        if False:
            print("request fail: {}, msg: {json_data.get('msg', 'No message found')}" % response.status_code)
        else:
            file_list = json_data.get('payload', [])
            diff_json = {}
            for file in file_list:
                if not file.get('binary'):
                    old_file_path = os.path.join(old_commit_floder, file.get('path'))
                    if not os.path.exists(os.path.dirname(old_file_path)):
                        os.makedirs(os.path.dirname(old_file_path))
                    with open(old_file_path, 'wb') as f:
                        f.write(file.get('content_old'))
                        # json.dump(file.get('content_old'), f)
                    new_file_path = os.path.join(new_commit_floder, file.get('path'))
                    if not os.path.exists(os.path.dirname(new_file_path)):
                        os.makedirs(os.path.dirname(new_file_path))
                    with open(new_file_path, 'wb') as f:
                        f.write(file.get('content_new'))
                        # json.dump(file.get('content_new'), f)
                    diff_content = file.get('diff')
                    matches = re.findall(r'\+(\d+(?:,\d+)?)', diff_content)
                    result_by_line = []
                    current_line = []

                    for match in matches:
                        if ',' in match:
                            current_line.extend(map(int, match.split(',')))
                            current_line[1] = current_line[0]+current_line[1]-1
                        else:
                            current_line.append(int(match))
                        result_by_line.append(current_line)
                        current_line = []
                    diff_json[file.get('path')] = result_by_line
            with open('tools/diff.json', 'w') as f:
                json.dump(diff_json, f, indent=2)

            subprocess.call(['ArchReviewer', '--kind=archinfo', '--list=git_repo.txt'])

            if os.path.exists(result_file_path):
                with open(result_file_path, 'r') as file:
                    try:
                        json_data = json.load(file)
                        result_json.append(json_data)
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON: {}" % e)
                        # abort(500)
            else:
                print("File not found: {%s}" % result_file_path)
                # abort(500)
    ret = {"status": 0, "msg": "", "payload": result_json}
    return jsonify(ret)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    app.run(host=IP, port=int(PORT), debug=True)
