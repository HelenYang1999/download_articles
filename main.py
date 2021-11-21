import numpy as np
import re
from urllib.request import urlopen #用于获取网页
from bs4 import BeautifulSoup #用于解析网页
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
import utils
import logging


def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


#arXiv获得文章pdf的方法
#url = 'https://arxiv.org/pdf/1512.03012.pdf'
# 其中序号可以从pdf中获得
def search_arxiv(driver,path,ids,titles_arXiv,logger):
    filenames_match_arXiv = {}
    download_urls = {}
    for i, id in enumerate(ids):
        base_url = 'https://arxiv.org/pdf/'
        url = base_url + id + '.pdf'
        driver.get(url)
        filenames_match_arXiv[id] = utils.legal_file_name(titles_arXiv[i])
        logger.info(titles_arXiv[i] + "成功下载")
        download_urls[titles_arXiv[i]] = url
        # 下载完成
    logger.info("arxiv网站搜索完成")
    time.sleep(100)
    utils.rename(path, filenames_match_arXiv,logger)
    return download_urls

def write_download_url(download_urls):
    urlfile = 'url.txt'
    with open(urlfile, mode='w', encoding='utf-8') as f:
        for item in download_urls:
            f.write(item)
            f.write(" ")
            f.write(download_urls[item])
            f.write('\n')
        logger.info("成功将论文对应下载地址写入"+urlfile+"中")

def set_chrome_driver(path):
    # 模拟登陆IEEE搜索网站
    # 设置无头
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # 如果不加这个选项，有时定位会出现问题
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def login_IEEE(driver):
    url = 'https://ieeexplore.ieee.org/servlet/wayf.jsp?entityId=https://idp.xmu.edu.cn/idp/shibboleth&url=https%3A%2F%2Fieeexplore.ieee.org%2FXplore%2Fguesthome.jsp%3Fsignout%3Dsuccess'
    # url = 'https://idp.xmu.edu.cn/idp/profile/SAML2/Redirect/SSO?execution=e1s1'
    driver.get(url)
    username = driver.find_element_by_id('username')
    # 添加自己的username
    username.send_keys("")
    password = driver.find_element_by_id('password')
    # 添加自己的password
    password.send_keys("")
    login_button = driver.find_element_by_xpath('/html/body/div/div/div/div[1]/form/div[5]/button')
    login_button.click()
    driver.implicitly_wait(3)

    window = driver.current_window_handle
    accept = driver.find_element_by_xpath('/html/body/form/div/div[2]/p[2]/input[2]')
    accept.send_keys(Keys.ENTER)
    # accept.submit()
    driver.implicitly_wait(6)
    logger.info("成功登陆IEEE网站")

def search_IEEE(driver,path,titles, conferences,logger):
    search_window = driver.current_window_handle
    filenames_match = {}
    download_urls = {}
    for i,conference in enumerate(conferences):
        try:
            # title = 'Multi-view 3D object detection network for autonomous driving'
            # conference = ' in CVPR, 2017'
            search_content = titles[i]+conferences[i]
            search_input = driver.find_element_by_xpath('//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/xpl-header/div/div[4]/xpl-search-bar-migr/div/form/div[2]/div/div/xpl-typeahead-migr/div/input')
            search_input.send_keys(search_content)

            search_button = driver.find_element_by_xpath('//*[@id="LayoutWrapper"]/div/div/div/div[3]/div/xpl-root/xpl-header/div/div[4]/xpl-search-bar-migr/div/form/div[3]/button')
            search_button.click()
            driver.implicitly_wait(2)

            result_window = driver.current_window_handle

            pdf_icon = driver.find_element_by_class_name("icon-pdf")
            pdf_icon.click()
            driver.implicitly_wait(2)
        except Exception:
            logger.warning(titles[i]+conferences[i]+"未成功搜索到")
            driver.back()
        else:
            try:
                download_window = driver.current_window_handle
                iframe = driver.find_element_by_xpath('/html/body/iframe')
                frame = driver.switch_to.frame(iframe)

                a = driver.find_element_by_xpath('//*[@id="main-content"]/a')
                download_url = a.get_attribute('href')
                download_urls[titles[i]] = download_url

                print(download_url)
                driver.get(download_url)
                driver.switch_to.default_content()
                logger.info(titles[i] + "成功下载")

                # 提取出下载后的文件名
                file_name = utils.get_number(download_url)
                new_file_name = utils.legal_file_name(titles[i])
                filenames_match[file_name] = new_file_name

            except Exception:
                logger.warning(titles[i]+"未成功下载")
            finally:
                driver.back()

    #迂回简单的方法，进行重命名，用一个dict结构实现filenames_match
    logger.info("IEEE网站搜索完成")
    time.sleep(50)
    utils.rename(path,filenames_match,logger)
    return download_urls

if __name__ == '__main__':
    #设置日志
    logger = logger_config(log_path='log.txt', logging_name='python main.py')
    #提取文章名称
    (titles, conferences, titles_arXiv, ids) = utils.get_titles()
    logger.info("完成数据的转换和写入")

    path = 'd:\\download_files\\'
    driver = set_chrome_driver(path)

    #开始IEEE的搜索
    login_IEEE(driver)
    download_urls_IEEE = search_IEEE(driver,path,titles, conferences,logger)
    time.sleep(10)

    #开始arXiv的搜索
    download_urls_arxiv = search_arxiv(driver,path,ids,titles_arXiv,logger)
    #将下载地址写入文件中
    all_download_urls = download_urls_IEEE + download_urls_arxiv
    # all_download_urls = download_urls_arxiv
    write_download_url(all_download_urls)

    time.sleep(10)
    driver.quit()

#todo 有个问题，当遇到网络不稳定的时候，需要延时，再多尝试几次

