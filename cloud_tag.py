import os
import jieba
import jieba.analyse
from wordcloud import WordCloud

def getJobDescriptionByPathList(path_list):
    """
    Args: path_list: [path1, path2, path3 ...]
            \path1
                1.txt
                2.txt
                ...
            \path2
                1.txt
                2.txt
                ...
            ...
    """
    job_descriptions = ""
    for path in path_list:
        for file in os.listdir(path):
            content_file = os.path.join(path, file)
            if os.path.isfile(content_file):
                with open(content_file) as jdf:
                    job_descriptions += jdf.read() + '\n'
    return job_descriptions

def getTagsByContent(content, topK=100):
    """返回content的关键词, TF-IDF算法
    """
    jieba.load_userdict('user_dict.txt')
    tags = jieba.analyse.extract_tags(content, topK=topK, withWeight=True, allowPOS=('n'))
    return tags

def getTagsByPathList(path_list):
    """返回目录列表下所有文档在一起的关键词
    Args: path_list: [文件目录1, 文件目录2, 文件目录3 ...]
    """
    job_descriptions  = getJobDescriptionByPathList(path_list)
    return getTagsByContent(job_descriptions)

def getTagsByPath(path):
    """返回目录下所有文档在一起的关键词
    Args: path_list: 文件目录
    """
    job_descriptions = getJobDescriptionByPathList([path])
    return getTagsByContent(job_descriptions)

if __name__ == '__main__':
    # 目标文件路径
    folder = 'data'
    sub_folder = ["机器学习", "数据挖掘", "算法"]
    path_list = []
    tags_list = []
    # 获取每个分类jd的关键词
    for kw in sub_folder:
        job_desc_folder = os.path.join(folder, kw, 'job_description')
        path_list.append(job_desc_folder)
        tags = getTagsByPath(job_desc_folder)
        tags_list.append(tags)
    # 获取所有分类在一起的关键词
    tags_all = getTagsByPathList(path_list)
    tags_list.append(tags_all)
    # 遍历关键词, 生成云标签并保存
    for i in range(len(tags_list)):
        tags = tags_list[i]
        tag_dic = {}
        for tag, weight in tags:
            tag_dic[tag] = weight
        wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", \
                                width=1300, height=800).fit_words(tag_dic)
        # plt.imshow(wordcloud)
        # plt.axis("off")
        # plt.show()
        if i < len(sub_folder):
            wordcloud.to_file('%s.png' % sub_folder[i])
        else:
            wordcloud.to_file('All.png')
