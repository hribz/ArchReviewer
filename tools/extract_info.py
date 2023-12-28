# coding: utf-8

import codecs
from BeautifulSoup import BeautifulSoup  # 在 Python 2 中使用 BeautifulSoup 库
import json

# 读取HTML文件内容
with codecs.open('/home/xiaoyu/github/ArchReviewer/tools/intrinsics.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

with open('/home/xiaoyu/github/ArchReviewer/tools/arch_info.json', 'r') as fd:
    json_db = json.load(fd)
    fd.close()
    json_db["x86"]["intrinsics"] = []

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content)

# 找到所有匹配的 <div class="intrinsic*">
intrinsic_divs = soup.findAll('div', {'class': lambda x: x and x.startswith('intrinsic')})

# 遍历处理每个 intrinsic div
for intrinsic_div in intrinsic_divs:
    # 提取 rettype 和 name
    rettype = intrinsic_div.find('span', {'class': 'rettype'}).text.strip()
    name = intrinsic_div.find('span', {'class': 'name'}).text.strip()

    # 打印结果
    print "rettype:", rettype
    print "name:", name
    print "---"

    if json_db["x86"]["intrinsics"] is not None:
        json_db["x86"]["intrinsics"].append(name)

if json_db["x86"]["intrinsics"] is not None:
    print(json_db["x86"]["intrinsics"])
    fd = open('/home/xiaoyu/github/ArchReviewer/tools/arch_info.json', 'w') 
    json.dump(json_db, fd, indent=2)
    fd.close()
