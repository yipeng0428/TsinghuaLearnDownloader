    # -*- coding: utf-8 -*-
import urllib2,urllib,cookielib,os
from bs4 import BeautifulSoup
from time import sleep

username=raw_input("input username or student number:")
password=raw_input("input password:")
file_size_limit=100    #文件大小限制，单位:M
operate=''
courses=[]
cj=cookielib.LWPCookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
params={'userid':username,'userpass':password,'submit1':'登录'}
print ('login...')
req=urllib2.Request("http://learn.tsinghua.edu.cn/use_go.jsp",urllib.urlencode(params))
operate=opener.open(req)
if "loginteacher_action" in operate.read():
    print("Login Successful!")
else:
    print("Login Failed!")

def getHtml(url):
    req=urllib2.Request(url)
    operate=opener.open(req)
    return BeautifulSoup(operate.read())

def downFile(url,dirname):
    req=urllib2.Request(url)
    operate=opener.open(req)
    filename=operate.headers['Content-Disposition'].split('"')[-2].decode('gbk')
    filesize=operate.headers['Content-Length']
    print(filename,filesize)
    if file_size_limit>0 and int(filesize)<(file_size_limit*1024*1024*1024):
        print "Donwloading",filename
        f=file(filename,"w")
        f.write(operate.read())
        f.close()
    else:
        print "Skip downloading",filename

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
        tr1=self.hwsoup.find_all('tr',"tr1")
        tr2=self.hwsoup.find_all('tr',"tr2")
        tr1.extend(tr2)
        for hw in tr1:
            try:
                hwpage=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/"+hw.a['href'])
                name=hw.a.text.strip()
                dlurl=hwpage.find_all("a")#attrs={"target","_top"})
                print(dlurl.__len__())
                for url in dlurl:
                    downFile("http://learn.tsinghua.edu.cn"+url['href'],dirpath)
            except Exception, e:
                print e.message
              #  pass
        os.chdir("../")

soup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2")
courses=soup.findAll(attrs={"width":"55%"})
print '共有',courses.__len__(),'门课程需要下载'
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
        c.getLtDownload()
        c.getHwDownload()
        sleep(60)
    except Exception,e:
        print  e.message
        sleep(180)

