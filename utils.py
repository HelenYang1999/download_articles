import re
import os
import time


def rename(path, filenames_match,logger):
    try:
        for item in filenames_match:
            old_name = path + item + '.pdf'
            print(old_name)
            new_name = path + filenames_match[item] + '.pdf'
            print(new_name)
            if os.path.exists(old_name):
                os.rename(old_name, new_name)
        logger.info("论文重命名成功")
    except Exception:
        logger.error("论文重命名失败")
        file = 'name_mapping.txt'
        with open(file, mode='a', encoding='UTF-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            for item in filenames_match:
                f.write(item)
                f.write(" ")
                f.write(filenames_match[item])
                f.write("\n")
            logger.info("成功将文件名对应关系保存在"+file+"中")

def before_get_titles():
    readfile = "ref.txt"
    writefile = "title.txt"
    allcontent = ''
    titles = []
    with open(readfile, mode='r', encoding='utf-8')as f:
        for line in f:
            allcontent += line.strip()
    rule = r'“(.*?)”'
    results = re.findall(rule, allcontent)

    with open(writefile, mode='w', encoding='utf-8') as f:
        for result in results:
            title = result[:-1]
            titles.append(title)
            f.write(title + '\n')
        # print("成功将文章名称写入" + writefile + "中\n")
    return titles


def before_get_conferences():
    readfile = "ref.txt"
    writefile = "conference.txt"
    allcontent = ''
    conferences = []
    with open(readfile, mode='r', encoding='utf-8')as f:
        for line in f:
            allcontent += line.strip()
    rule = r'”(.*?)\.'
    results = re.findall(rule, allcontent)

    with open(writefile, mode='w', encoding='utf-8') as f:
        for result in results:
            conferences.append(result)
            f.write(result + '\n')
        # print("成功将文章名称写入" + writefile + "中\n")
    return conferences

def get_all_content(readfile):
    allcontent = ''
    with open(readfile, mode='r', encoding='utf-8')as f:
        for line in f:
            allcontent += line.strip()
    return allcontent

def write_data_to_file(filename,datas):
    with open(filename, mode='w', encoding='utf-8') as f:
        for data in datas:
            f.write(data + '\n')
    # print("完成" + filename + "的数据写入\n")

def get_titles():
    readfile = "ref.txt"
    titlefile = "title.txt"
    conferencefile = "conference.txt"
    titleArXivfile = "title_arXiv.txt"
    idfile = "id_arXiv.txt"

    allcontent = get_all_content(readfile)

    articles = allcontent.split('[')[1:]
    rule_of_arXiv = r'arXiv'
    rule_of_title = r'“(.*?)”'
    rule_of_conference = r'”(.*?)\.'
    rule_of_id = r'arXiv:(.*?),'
    titles = []
    conferences = []
    ids = []
    titles_arXiv = []
    for article in articles:
        if bool(re.search(rule_of_arXiv,article)):
            #arXiv论文
            title_arXiv = re.findall(rule_of_title, article)[0][:-1]
            id = re.findall(rule_of_id, article)[0]
            titles_arXiv.append(title_arXiv)
            ids.append(id)
        else:
            title = re.findall(rule_of_title, article)[0][:-1]
            conference = re.findall(rule_of_conference, article)[0]
            titles.append(title)
            conferences.append(conference)
    write_data_to_file(titlefile, titles)
    write_data_to_file(conferencefile, conferences)
    write_data_to_file(titleArXivfile, titles_arXiv)
    write_data_to_file(idfile, ids)

    return titles,conferences,titles_arXiv,ids

def get_number(url):
    # url = 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=8954194&ref=aHR0cHM6Ly9pZWVleHBsb3JlLmllZWUub3JnL3NlYXJjaC9zZWFyY2hyZXN1bHQuanNwP25ld3NlYXJjaD10cnVlJnF1ZXJ5VGV4dD1Nb2RlbGluZyUyMHBvaW50JTIwY2xvdWRzJTIwd2l0aCUyMHNlbGYtYXR0ZW50aW9uJTIwYW5kJTIwZ3VtYmVsJTIwc3Vic2V0JTIwc2FtcGxpbmcsJTIwaW4lMjBDVlBSLCUyMDIwMTk='
    rule = r'&arnumber=(.*?)&ref='
    number = re.findall(rule, url)[0]
    lenth = len(number)
    file_name = ""
    if lenth < 8:
        for i in range(8 - lenth):
            file_name = file_name + "0"
    file_name = file_name + number

    return file_name

def legal_file_name(file_name):
    illegal_chars = ["\\", "/", ":", "?", "\"", "<", ">", "|"]
    for illegal_char in illegal_chars:
        file_name = file_name.replace(illegal_char, "")
    return file_name

if __name__ == '__main__':
    # url = 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=8765737&ref=aHR0cHM6Ly9pZWVleHBsb3JlLmllZWUub3JnL3NlYXJjaC9zZWFyY2hyZXN1bHQuanNwP25ld3NlYXJjaD10cnVlJnF1ZXJ5VGV4dD1TdGVyZW8lMjBtYXRjaGluZyUyMHVzaW5nJTIwbXVsdGktbGV2ZWwlMjBjb3N0JTIwdm9sdW1lJTIwYW5kJTIwbXVsdGktc2NhbGUlMjBmZWF0dXJlJTIwY29uc3RhbmN5JTIwSUVFRSUyMFRQQU1JLCUyMDIwMTk='
    # file_name = get_number(url)
    # get_titles()
    title = "dsjnjs/dsnjd\dfdfmk:dsndj?dsjn<dsdnjs|d   snd "
    newtitle = legal_file_name(title)
    print(newtitle)
