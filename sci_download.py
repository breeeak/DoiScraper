# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 20:37
# @Author  : Marshall
# @FileName: sci_download.py
"""
此应用程序用于教育目的。仅供学术交流，请勿从事任何违法活动！
利用了scihub，有能力的同学可以赞助一下，或者访问出版社下载阅读正版文章！
作者不承担任何责任！！！
"""
import requests
from bs4 import BeautifulSoup
import os
import re
import time
import random


def parse_title(title):
    # 这里处理的都是这种格式： Venkatesan, H., Chen, J., Liu, H., Liu, W., Hu, J., A Spider-Capture-Silk-Like Fiber with Extremely High-Volume Directional Water Collection. Advanced Functional Materials, 2020. 30(30). https://doi.org/10.1002/adfm.202002437 IF=16.836"
    # 所以用这种方式来提取的
    results = re.findall(r"https://(.+?)IF", title)
    if len(results) == 1:
        return str(results[0]).strip()
    else:
        return False


def main(paper_list_path, sci_hub_list=["https://sci-hub.yncjkj.com/"], is_parser=False):
    """
    :param paper_list_path: 要下载的文章列表
    :param sci_hub_list: 可用的sci hub 地址，如果这个地址不可以用了可以更新，最后要带个/
    :param is_parser: 要下载的文章列表，一行是一个文章doi,可以https://doi.org/开头，也可以去掉
    :return:
    """
    dest_path = "articles"
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    f = open(paper_list_path, "r", encoding="utf-8")
    # head是浏览器的头信息，请求载体的身份标识，使用这个可以的
    head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
    for doi in f.readlines():
        # 随机的隔一段时间下载，防止被封ip地址，这里设置的是15 到60秒之间的随机数进行下载，可以自己设置
        time.sleep(random.randint(15, 60))
        doi = doi[:-1]  # 去换行符
        if len(doi) == 0:
            continue
        if is_parser:
            doi = parse_title(doi)
            if not doi:
                continue
        for sci_hub_url in sci_hub_list:
            url = sci_hub_url + doi
            try:
                download_url = ""
                r = requests.get(url, headers=head)
                r.raise_for_status()
                r.encoding = r.apparent_encoding
                soup = BeautifulSoup(r.text, "html.parser")
                # 对于有的sci地址而言，会在右侧显示出文章的预览，而有的不会，这里分别处理这两种情况。
                # 获取pdf的下载地址
                if soup.iframe is None:  #
                    download_url = "https:" + soup.embed.attrs["src"]
                else:
                    download_url = soup.iframe.attrs["src"]
                print(doi + " is downloading...\n  --The download url is: " + download_url)
                # 进行下载
                download_r = requests.get(download_url, headers=head)
                download_r.raise_for_status()
                with open(os.path.join(dest_path, doi.replace("/", "_").replace(":", "_") + ".pdf"), "wb+") as temp:
                    temp.write(download_r.content)

                print(doi + " download successfully.\n")
            except:
                # 下载失败的话记录下载失败信息，这里用了一个新文件来保存
                with open("error.txt", "a+") as error:
                    error.write(doi + ": occurs error!\n")
                    # 如果获取到了下载地址，但是下载失败，记录这个地址
                    if "https://" in download_url:
                        error.write(" --The download url is: " + download_url + "\n\n")
    f.close()


if __name__ == '__main__':
    # 可用的sci hub 地址，如果这个地址不可以用了可以更新
    sci_hub_list = ["https://sci-hub.yncjkj.com/"]
    # 要下载的文章列表，一行是一个文章doi,可以https://doi.org/开头，也可以去掉
    paper_list_path = "doi.txt"
    # 运行主程序，is_parser是对于非十分标准的title情况处理，例如这里的样式。还包含了很多其他信息。一般传false，一行一个doi
    main(paper_list_path, sci_hub_list, is_parser=True)
