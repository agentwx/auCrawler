# -*- coding: utf-8 -*- 
'''
Created on 2013

@author: catsky
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
import setting
import time
import re


Base = declarative_base()


class ServerDB():
    def __init__(self):
        ServerDB.engine = None
        ServerDB.session = None

        if ServerDB.engine is None:
            if setting.DBCHOICE == 'mysql':
                ServerDB.engine = create_engine('mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8'
                                            %(setting.DBUSER_MYSQL, setting.DBPASSWORD_MYSQL,
                                              setting.HOSTNAME, setting.DBPORT_MYSQL,
                                              setting.DBNAME_MYSQL))
            elif setting.DBCHOICE == 'postgresql':
                ServerDB.engine = create_engine("postgresql://%s:%s@%s:%s/%s"
                                            %(setting.DBUSER_POSTGRES, setting.DBPASSWORD_POSTGRES,
                                              setting.HOSTNAME, setting.DBPORT_POSTGRES,
                                              setting.DBNAME_POSTGRES))

        Session = sessionmaker(bind=ServerDB.engine)
        if ServerDB.session is None:
            ServerDB.session = Session()

    def getSession(self):
        Base.metadata.create_all(ServerDB.engine)
        return ServerDB.session


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Queue('%s')>" % (self.url)


class DuplCheckDB(Base):
    __tablename__ = 'duplcheckDB'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<DuplCheckDB('%s')>" % (self.url)


class Webpage(Base):
    __tablename__ = 'webpage'
    id = Column(Integer, primary_key=True)
    url = Column(String(200))
    html = Column(Text)

    category = Column(String(17))
    title = Column(String(100))
    content = Column(Text)
    comment_num = Column(Integer)
    closecomment = Column(Integer)
    tags = Column(String(100))
    password = Column(String(8))
    add_time = Column(Integer)
    edit_time = Column(Integer)
    shorten_content = Column(Text)
    imgthumbnail = Column(String(200))
    post_type = Column(Integer)  # 1 for shown on top
    click_num = Column(Integer)  # 1 for shown on top
    editor_title = Column(String(100))
    source = Column(String(100))

    def __init__(self, url=None, html=None, title=None, content=None,
                 category=None, comment_num=0, closecomment=0, tags=None,
                 password=None, shorten_content=None, imgthumbnail=None,
                 post_type=0, add_time=0, edit_time=0, click_num=0,
                 editor_title=None, source=None):
        self.url = url
        self.html = html
        self.category = category
        self.title = title
        self.content = content
        self.comment_num = comment_num
        self.closecomment = closecomment
        self.tags = tags
        self.password = password
        self.add_time = add_time
        self.edit_time = edit_time
        self.shorten_content = shorten_content
        self.imgthumbnail = imgthumbnail
        self.post_type = post_type
        self.click_num = click_num
        self.editor_title = editor_title
        self.source = source

    def __repr__(self):
        return "<Webpage('%s','%s')>" % (self.url, self.html)


class OperatorDB:
    def __init__(self, serverDB=None):
        if serverDB is None:
            self.db = ServerDB()
        else:
            self.db = serverDB
        self.session = self.db.getSession()

    def add_seeds(self, links):
        new_links = []
        for link in links:
            if self.session.query(DuplCheckDB).filter_by(url=link).first() is None:
                new_links.append(link)

        for link in new_links:
            dc = DuplCheckDB(link)
            self.session.add(dc)

            queue = Queue(link)
            self.session.add(queue)

        self.session.commit()

    def pop_url(self):
        row = self.session.query(Queue).order_by("id").first()
        url = None
        if row is not None:
            print "in pop_url: row is not None. id: %s" % row.id
            url = row.url.strip()
            self.session.delete(row)
            self.session.commit()
            print "in pop_url: row is delted and commit"
        return url

    def html2db(self, url, html, title=None, addtime=None, source=None, content=None):
        if addtime is not None:
            t = time.strptime(addtime, '%Y-%m-%d %M:%S')
            addtime = time.mktime(t)

        if content is not None:
            shorten_content = self._shorten_content(content)
        else:
            shorten_content = None
        webpage = Webpage(url=url, html=html, title=title,
                          add_time=addtime, source=source,
                          content=content,
                          #shorten_content=self._shorten_content(content))
                          shorten_content=shorten_content)
        self.session.add(webpage)
        self.session.commit()

    def close(self):
        self.session.close()

    def _shorten_content(self, htmlstr='',sublength=80):
        return htmlstr[0:sublength]
#         print ">>>>: %s" % htmlstr
#         result = re.sub(r'<[^>]+>', '', unicode(htmlstr))
#         print ">>>>: %s" % result
#         result = result.replace("&nbsp;","")
#         print ">>>>: %s" % result
#         return result[0:5]

if __name__ == '__main__':
    dbop = OperatorDB()
    dbop.add_seeds(["http://www.baidu.com", "http://sinaapp.com"])
