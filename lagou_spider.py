from bs4 import BeautifulSoup
import html5lib
import requests
import json
import re
import jieba
import jieba.analyse
import os
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt

headers = {"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"}


def getTotalPageNumsByKw(kw="机器学习"):
    url = "https://www.lagou.com/jobs/positionAjax.json?first=false&pn=1&kd=%s" % kw
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    try:
        total_page = data["content"]['positionResult']["totalCount"] // 15
        if total_page > 30:
            total_page = 30
        return total_page
    except Exception as e:
        print("json解析错误:", e)
        return 0

def savePostionIdByKw(kw='机器学习', folder='data/机器学习'):
    # url:https://www.lagou.com/jobs/positionAjax.json?first=false&pn=4&kd=机器学习
    if not os.path.exists(folder):
        os.mkdir(folder)
    total_page_nums = getTotalPageNumsByKw(kw)
    with open(os.path.join(folder, 'positionId.txt'), 'w') as f:
        for i in range(1, total_page_nums+1):
            time.sleep(0.5)
            url = "https://www.lagou.com/jobs/positionAjax.json?first=false&pn=%d&kd=%s" % (i, kw)
            response = requests.get(url, headers=headers)
            data = json.loads(response.text)
            if data:
                try:
                    results = data["content"]['positionResult']["result"]
                except Exception as e:
                    print("json解析错误:", e)
                if results:
                    for result in results:
                        position_id = str(result['positionId'])
                        print(position_id + "," + result['positionName'])
                        f.write(position_id + '\n')

def getJdById(position_id):
    if not os.path.exists('job_description'):
        os.mkdir('job_description')

    url = "https://www.lagou.com/jobs/%s.html" % position_id
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html5lib")
    # 一下需要错误处理
    try:
        jd = soup.select("dd.job_bt > div")[0].text.strip()
    except Exception as e:
        print("selector解析错误", e)
        return ""
    return jd

def saveJobDescriotion(position_id_file, job_decs_folder):
    with open(position_id_file, 'r') as pif:
        for line in pif.readlines():
            position_id = line.strip()
            jd = os.path.join(job_decs_folder, position_id + '.txt')
            with open(jd, 'w') as jdf:
                jdf.write(getJdById(position_id))
                print('正在写入position_id为%s的job_description' % position_id)

def getJobDescriptionForTag(path_list):
    job_descriptions = ""
    for path in path_list:
        for file in os.listdir(path):
            with open(os.path.join(path, file)) as jdf:
                job_descriptions += jdf.read() + '\n'
    return job_descriptions

def getTagsByContent(content):
    jieba.load_userdict('user_dict.txt')
    # tags = jieba.analyse.extract_tags(content, topK=20, allowPOS=('n'))
    tags = jieba.analyse.textrank(content, topK=100, withWeight=True, allowPOS=('n'))
    return tags

def getTagsAll(path_list):
    job_descriptions  = getJobDescriptionForTag(path_list)
    return getTagsByContent(job_descriptions)

def getTagsByPath(path):
    job_descriptions = getJobDescriptionForTag([path])
    return getTagsByContent(job_descriptions)

if __name__ == "__main__":
    target = ["机器学习", "数据挖掘", "算法"] # ["机器学习", "数据挖掘", "算法"]
    folder = 'data'
    # 1.---------------创建各类别下的positionId文件------------------------
    # if not os.path.exists(folder):
    #     os.mkdir(folder)
    # for kw in target:
    #     savePostionIdByKw(kw=kw, folder=os.path.join(folder, kw))

    # 2.---------------分别读取各类positionId文件, 创建job_description------------
    # for kw in target:
    #     job_decs_folder = os.path.join(folder, kw, 'job_description')
    #     if not os.path.exists(job_decs_folder):
    #          os.mkdir(job_decs_folder)
    #     position_id_file = os.path.join(folder, kw, 'positionId.txt')
    #     saveJobDescriotion(position_id_file, job_decs_folder)

    # 3.-----------------关键词提取-----------------------------
    path_list = []
    for kw in target:
        job_decs_folder = os.path.join(folder, kw, 'job_description')
        path_list.append(job_decs_folder)
        # tags = getTagsByPath(job_decs_folder)
        # print(tags)
    tags_all = getTagsAll(path_list)
    # print(tags_all)
    # wordcloud = WordCloud(font_path="simhei.ttf", background_color="white").generate(",".join(tags_all))
    tag_dic = {}
    for tag, weight in tags_all:
        tag_dic[tag] = weight
    wordcloud = WordCloud(font_path="simhei.ttf", background_color="white").fit_words(tag_dic)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
