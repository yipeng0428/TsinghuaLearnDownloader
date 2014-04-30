    # -*- coding: utf-8 -*-
import requests,os,chardet
from bs4 import BeautifulSoup
from time import sleep
def getUTF8(str):
    strEncode=chardet.detect(str)
    return str.decode(strEncode['encoding']).encode('utf8')

def getUnicode(str):
    strEncode=chardet.detect(str)
    return str.decode(strEncode['encoding'])


print u'清华大学网络学堂下载器'
print u'在毕业之前抢救网络学堂上的资料----By Wu, Yongkai'


username=raw_input('input your id:   ')
password=raw_input("input your password:   ")

params={'userid':username,'userpass':password,'submit1':'登录'}
print ('login...')
req=requests.post("http://learn.tsinghua.edu.cn/use_go.jsp",data=params)
cookie=req.cookies
#print req.content



def getHtml(url):
    req=requests.get(url,cookies=cookie)
    return BeautifulSoup(req.content)

def downFile(url,dirname):
    req=requests.get(url,cookies=cookie)
    filename=req.headers['Content-Disposition'].split('"')[-2]
    filesize=req.headers['Content-Length']
    print "Donwloading",getUnicode(filename)
    f=file(filename,"w")
    f.write(req.content)
    f.close()


class Course:
    def __init__(self,id,name,ltsoup,hwsoup):
        self.id=id
        self.name=name
        self.ltsoup=ltsoup
        self.hwsoup=hwsoup

    def mkDir(self,basedir):
        os.chdir(basedir)
        if not os.path.isdir(self.name):
            print 'Start Donloading',self.name
            os.mkdir(self.name)
        dirpath= os.path.abspath(self.name)
        os.chdir(dirpath)

    def getLtDownload(self):
        if not os.path.isdir(u"课程文件"):
            os.mkdir(u"课程文件")
        dirpath= os.path.abspath(u"课程文件")
        os.chdir(dirpath)

        tr1=self.ltsoup.find_all('tr',"tr1")
        tr2=self.ltsoup.find_all('tr',"tr2")
        tr1.extend(tr2)
        for lt in tr1:
        	try:
	            url="http://learn.tsinghua.edu.cn"+lt.a['href']
	            name=lt.a.text.strip()
	            downFile(url,dirpath)
	        except Exception,e:
	        	pass
        os.chdir("../")

    def getHwDownload(self):
        if not os.path.isdir(u"课程作业"):
            os.mkdir(u"课程作业")
        dirpath= os.path.abspath(u"课程作业")
        os.chdir(dirpath)
        tr1=self.hwsoup.find_all(attrs={'class':"tr1"})
        #print len(tr1)
        tr2=self.hwsoup.find_all(attrs={'class':'tr2'})
        tr1.extend(tr2)
        for hw in tr1:
            try:
                hwpage=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/"+hw.a['href'])
                name=hw.a.text.strip()
                dlurl=hwpage.find_all("a")#,attrs={"target","_top"})
                for url in dlurl:
                    downFile("http://learn.tsinghua.edu.cn"+url['href'],dirpath)
            except Exception, e:
                print e.message
              #  pass
        os.chdir("../")

if 'window.location = "loginteacher_action.jsp";' not in req.content:
    print u'登录错误,10s后自动退出'
    sleep(10)
else:
    soup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2")
    courses=soup.findAll(attrs={"width":"55%"})
    print u'共有',courses.__len__(),u'门课程需要下载'
    basedir=os.path.dirname(os.path.abspath("__file__"))
    for course in courses[2::]:
        try:

            course_url=course.a["href"]
            course_name=course.a.text.strip()
            course_id=course_url.split("=")[-1]
            ltsoup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id="+str(course_id))
            hwsoup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id="+str(course_id))
            c=Course(course_id,course_name,ltsoup,hwsoup)
            c.mkDir(basedir)
            c.getHwDownload()
            c.getLtDownload()
            sleep(60)
        except Exception,e:
            print  e.message
            sleep(180)

