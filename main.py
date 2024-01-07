import json
import logging
import os
import threading
import time
from typing import Optional, List
import re

from flask import Flask, request, abort
from nacos_py import NacosService, NacosClient
from dotenv import load_dotenv
import subprocess
import requests
import shutil

IP = "localhost"
PORT = "12499"

NACOS_ENABLE = False

SERVER_ADDRESSES = "http://IP:PORT"
NAMESPACE = "namespace"
CLIENT: Optional[NacosClient] = None
SERVICE_NAME = "inference"

NAME = "service"  # Nacos用户名
PWD = "pwd"  # Nacos密码

# Nacos 配置管理
config = {
    "GITHUB_TOKEN": "",
    "OPENAI_API_KEY": "",
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": ""
}


class Inference(Flask):
    def __init__(self, *args, **kwargs):
        super(Inference, self).__init__(*args, **kwargs)


app = Inference(__name__)


def heartbeat():
    while True:
        CLIENT.send_heartbeat("DEFAULT_GROUP@@" + SERVICE_NAME, IP, PORT)
        time.sleep(3)


def updated_config():
    global config
    data_id = "inference.json"
    config = json.loads(CLIENT.get_config(data_id, "DEFAULT_GROUP", no_snapshot=True))
    for _config in config.keys():
        os.environ[_config] = config[_config]


@app.route("/inference", methods=["POST"])
def inference():
    """
    请求格式:
    POST /inference?repository={repository_id}
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
    返回格式:
    [
    {
        "result": "arm",
        "detail": {
            "file_path_new_1": {
                "arch_line": [
                    "行号", "行号1-行号2", ...
                ],
                "comments": {
                    "行号（变更后）": "单行注释内容",
                    "起始行号-结束行号": "多行注释内容"
                },
            },
            "file_path_new_2": {
                "arch_line": [
                    "行号", "行号1-行号2", ...
                ],
                "comments": {
                    "行号（变更后）": "单行注释内容",
                    "起始行号-结束行号": "多行注释内容"
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
    name = request.args.get('repository', None)
    commits = []
    try:
        raw_data = request.get_data(as_text=True)
        commits = json.loads(raw_data)
        if name is None or len(commits) == 0 or type(commits) != list:
            raise Exception()
        for commit in commits:
            if type(commit) != dict:
                raise Exception()
    except:
        abort(400)
    if NACOS_ENABLE:
        updated_config()

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
        params = {'repo_id': commit.get('repo_id'), 'commit_hash': commit.get(hash)}
        response = requests.get('http://127.0.0.1:12888/api/file', params=params)
        json_data = response.json()
        # 检查请求是否成功
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}, msg: {json_data.get('msg', 'No message found')}")
        else:
            file_list = json_data.get('payload', [])
            diff_json = []
            for file in file_list:
                if not file.get('binary'):
                    with open(os.path.join(old_commit_floder, file.get('path')), 'w') as f:
                        f.write(file.get('content_old'))
                    with open(os.path.join(new_commit_floder, file.get('path')), 'w') as f:
                        f.write(file.get('content_new'))
                    diff_content = file.get('diff')
                    matches = re.findall(r'\+(\d+(?:,\d+)?)', diff_content)
                    result_by_line = []
                    current_line = []

                    for match in matches:
                        if ',' in match:
                            current_line.extend(map(int, match.split(',')))
                        else:
                            current_line.append(int(match))
                        result_by_line.append(current_line)
                        current_line = []
                    diff_json.append({file.get('path'): result_by_line})
            with open('tools/diff.json', 'w') as f:
                f.write(diff_json)

            subprocess.call(['ArchReviewer', '--kind=archinfo', '--list=git_repo.txt'])

            if os.path.exists(result_file_path):
                with open(result_file_path, 'r') as file:
                    try:
                        json_data = json.load(file)
                        result_json.append(json_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        # abort(500)
            else:
                print(f"File not found: {result_file_path}")
                # abort(500)
    return result_json

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    if NACOS_ENABLE:
        CLIENT = NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username=NAME, password=PWD)
        NacosService(SERVICE_NAME, CLIENT).register(IP, PORT)
        heart = threading.Thread(target=heartbeat)
        heart.start()
    app.run(host=IP, port=int(PORT), debug=True)
