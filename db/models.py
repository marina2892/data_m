from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()

tag_post = Table('tag_post',
                 Base.metadata,
                 Column('id_post', Integer, ForeignKey('post.id')), 
                 Column('id_tag', Integer, ForeignKey('tag.id'))
                 )

class Post(Base):
    __tablename__ = 'post'
    
    id = Column(Integer, primary_key = True, autoincrement = True)
    url = Column(String, nullable = False, unique = True)
    title = Column(String)
    url_img = Column(String, nullable = False)
    date = Column(String)
    id_writer = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates = 'posts')
    
    comments = relationship('Comment', back_populates = 'post')
    tags = relationship('Tag', secondary = tag_post)
   
class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String)
    url = Column(String, nullable = False, unique = True)
    posts = relationship('Post', back_populates = 'writer')
    
class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String)
    url = Column(String, nullable = False, unique = True)
    posts = relationship('Post', secondary = tag_post)
    
class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key = True, autoincrement = True)
    auth = Column(String)
    text = Column(String)
    id_post = Column(Integer, ForeignKey('post.id'))
    post = relationship('Post', back_populates = 'comments')
    
