# -*- coding: utf-8 -*-
import chardet
import os
import requests
from bs4 import BeautifulSoup
from time import sleep


site = 'http://learn.tsinghua.edu.cn'


def to_unicode(text):
    if type(text) == unicode:
        return text
    encoding = chardet.detect(text)
    return text.decode(encoding['encoding'])


def safe_name(text):
    return text.replace('/', '-').replace('\\', '-')


def ext_name(name):
    ext = ''
    while name.rfind('.') > 0:
        pos = name.rfind('.')
        if len(name[pos:]) < 8:
            ext = name[pos:] + ext
            name = name[:pos]
        else:
            break
    return ext


def download_file(url, name, has_ext=False):
    req = requests.get(url, cookies=cookie)
    filename = safe_name(name)
    if not has_ext:
        filename = filename + ext_name(req.headers['Content-Disposition'].split('"')[-2])
    open(filename.encode('utf-8'), 'w').write(req.content)


def is_list_item(tag):
    if not tag.has_attr('class'):
        return False
    clazz = tag['class'][0]
    return clazz == 'tr1' or clazz == 'tr2'


class Page:
    def __init__(self, url, local_name, visit_sub_pages=None, download_files=None):
        local_name = safe_name(local_name)
        if visit_sub_pages or download_files:
            if not os.path.isdir(local_name):
                os.mkdir(local_name)
            os.chdir(os.path.abspath(local_name))
        soup = BeautifulSoup(requests.get(site + url, cookies=cookie).content, 'html5lib')

        metatag = soup.new_tag('meta')
        metatag.attrs['charset'] = 'utf-8'
        soup.head.append(metatag)
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('img')]
        # show tab contents in file list page
        for tag in soup.findAll('div', 'layerbox'):
            del(tag['style'])

        open(local_name + '.htm', 'w').write(soup.prettify('utf-8'))
        if visit_sub_pages:
            visit_sub_pages(soup)
        if download_files:
            download_files(soup)
        if visit_sub_pages or download_files:
            os.chdir('../')


class HomePage(Page):
    def __init__(self):
        def visit_sub_pages(soup):
            for course in soup.findAll(attrs={'width': '55%'})[2:]:
                link = course.a['href']
                course_id = link.split('=')[-1]
                CoursePage(course_id, course.a.text.strip())

        Page.__init__(self,
                      '/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2',
                      u'课程列表',
                      visit_sub_pages)


class CoursePage(Page):
    def __init__(self, course_id, course_name):
        print course_name
        Page.__init__(self,
                      '/MultiLanguage/lesson/student/course_info.jsp?course_id=' + course_id,
                      course_name,
                      visit_sub_pages=lambda soup: [
                          AnnouncementListPage(course_id),
                          DiscussionListPage(course_id),
                          HomeWorkListPage(course_id),
                          FileListPage(course_id),
                      ])


class DiscussionListPage(Page):
    def __init__(self, course_id):
        def visit_sub_pages(soup):
            trs = soup.findAll(is_list_item)
            trs.reverse()
            id = 1
            for tr in trs:
                Page('/MultiLanguage/public/bbs/' + tr.a['href'],
                     str(id))
                id += 1
        Page.__init__(self,
                      '/MultiLanguage/public/bbs/gettalkid_student.jsp?course_id=' + course_id,
                      u'课程讨论',
                      visit_sub_pages=visit_sub_pages)


class AnnouncementListPage(Page):
    def __init__(self, course_id):
        def visit_sub_pages(soup):
            for tr in soup.findAll(is_list_item):
                link = '/MultiLanguage/public/bbs/' + tr.a['href']
                name = tr.contents[1].getText()
                Page(link, name)
        Page.__init__(self,
                      '/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id=' + course_id,
                      u'课程公告',
                      visit_sub_pages)


class FileListPage(Page):
    def __init__(self, course_id):
        def download_files(soup):
            for tr in soup.findAll(is_list_item):
                link = tr.a['href']
                name = tr.a.getText().strip()
                print u'  下载课件 ' + name + ' (' + tr.contents[9].getText().strip() + ')'
                download_file(site + link, name)

        Page.__init__(self,
                      '/MultiLanguage/lesson/student/download.jsp?course_id=' + course_id,
                      u'课程文件',
                      download_files=download_files)


class HomeWorkListPage(Page):
    def __init__(self, course_id):
        def visit_sub_pages(soup):
            for tr in soup.findAll(is_list_item):
                link = '/MultiLanguage/lesson/student/' + tr.a['href']
                name = tr.a.getText().strip()
                size = tr.contents[9].contents[0].strip()
                print u'  下载作业 ' + name + ' (' + size + ')'
                HomeWorkPage(link, name)
        Page.__init__(self,
                      '/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id=' + course_id,
                      u'课程作业',
                      visit_sub_pages=visit_sub_pages)


class HomeWorkPage(Page):
    def __init__(self, url, name):
        def download_files(soup):
            for a in soup.findAll('a'):
                download_file(site + a['href'], a.contents[0], has_ext=True)
        Page.__init__(self, url, name,
                      download_files=download_files)

print u'清华大学网络学堂下载器'

username = raw_input('input your id:   ')
password = raw_input("input your password:   ")

params = {'userid': username, 'userpass': password, 'submit1': '登录'}
print ('login...')
login_request = requests.post("http://learn.tsinghua.edu.cn/use_go.jsp", data=params)

cookie = login_request.cookies

if 'window.location = "loginteacher_action.jsp";' not in login_request.content:
    print u'登录失败'
else:
    HomePage()
