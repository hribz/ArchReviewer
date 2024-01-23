# -*- coding: UTF-8 -*-
import json
import logging
import os
import threading
import time
from typing import Optional, List
import re

from flask import Flask, request, abort, jsonify
from nacos_py import NacosService, NacosClient
from dotenv import load_dotenv
import subprocess
import requests
import shutil
import random

IP = "localhost"
PORT = "12499"

NACOS_ENABLE = True

SERVER_ADDRESSES = "http://localhost:8848"
NAMESPACE = "public"
CLIENT: Optional[NacosClient] = None
SERVICE_NAME = "sa"

NAME = "nacos"  # Nacos用户名
PWD = "nacos"  # Nacos密码

config = {
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": ""
}

def heartbeat():
    while True:
        CLIENT.send_heartbeat("DEFAULT_GROUP@@" + SERVICE_NAME, IP, PORT)
        time.sleep(3)

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
if NACOS_ENABLE:
    CLIENT = NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username=NAME, password=PWD)
    NacosService(SERVICE_NAME, CLIENT).register(IP, PORT)
    heart = threading.Thread(target=heartbeat, daemon=True)
    heart.start()

class Inference(Flask):
    def __init__(self, *args, **kwargs):
        super(Inference, self).__init__(*args, **kwargs)


app = Inference(__name__)

def get_service(service_name):
    instances = CLIENT.list_naming_instance(service_name, namespace_id=NAMESPACE, healthy_only=True)
    if len(instances["hosts"][0]) == 0:
        raise Exception("服务调用异常:没有找到指定服务-%s" % service_name)
    # 负载均衡
    host = random.choice(instances["hosts"])
    return host["ip"], host["port"]

def updated_config():
    global config
    data_id = "inference.json"
    config = json.loads(CLIENT.get_config(data_id, "DEFAULT_GROUP", no_snapshot=True))
    for _config in config.keys():
        os.environ[_config] = config[_config]

def get_commit_info(repository_id, commit_id):
    service_ip, service_port = get_service("backend")
    params = {
        "repo_id": repository_id,
        "commit_hash": commit_id
    }
    result = requests.get(f"http://{service_ip}:{service_port}/api/file", params=params)
    if result.status_code != 200:
        raise Exception(f"服务调用异常:调用失败-{result.status_code}")
    return result

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
        response = get_commit_info(commit['repo_id'], commit['hash'])
        json_data = json.loads(response.text)
        if os.path.exists(new_commit_floder):
            shutil.rmtree(new_commit_floder)
            os.makedirs(new_commit_floder)
        if os.path.exists(old_commit_floder):
            shutil.rmtree(old_commit_floder)
            os.makedirs(old_commit_floder)
        # print (response.text)
        # with open('file_list.json', 'r') as f:
        #     json_data = json.load(f)
        # check request status
        if response.status_code != 200:
        # if False:
            print("request fail: {}, msg: {json_data.get('msg', 'No message found')}" % response.status_code)
        else:
            file_list = json_data.get('payload', [])
            diff_json = {}
            for file in file_list:
                if not file.get('binary'):
                    if file.get('content_old'):
                        old_file_path = os.path.join(old_commit_floder, file.get('path'))
                        if not os.path.exists(os.path.dirname(old_file_path)):
                            os.makedirs(os.path.dirname(old_file_path))
                        with open(old_file_path, 'w') as f:
                            f.write(file.get('content_old'))
                            # json.dump(file.get('content_old'), f)
                    if file.get('content_new'):
                        new_file_path = os.path.join(new_commit_floder, file.get('path'))
                        if not os.path.exists(os.path.dirname(new_file_path)):
                            os.makedirs(os.path.dirname(new_file_path))
                        with open(new_file_path, 'w') as f:
                            f.write(file.get('content_new'))
                            # json.dump(file.get('content_new'), f)
                    if file.get('diff'):
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
                result_json.append({"result": "", "detail": {}})
                # abort(500)
    # ret = {"status": 0, "msg": "", "payload": result_json}
    print (len(result_json))
    return result_json

if __name__ == '__main__':
    app.run(host=IP, port=int(PORT), debug=True)
