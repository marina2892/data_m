from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models

class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind = engine)
        self.maker = sessionmaker(bind = engine) 
    
    def _get_or_create(self, session, model, **data0): 
        db_data = session.query(model).filter(model.url == data0['url']).first()
        
        if not db_data:
            db_data = model(**data0)
            session.add(db_data)
        return db_data
    
    def create_post(self, data):
        session = self.maker()
        writer = self._get_or_create(session, models.Writer, **data['writer_data'])
        tags_list = data.get('tags_data')
        tags = list(map(lambda tag_data: self._get_or_create(session, models.Tag, **tag_data), tags_list))
        
        post_data = data.get('post_data')
        post = self._get_or_create(session, models.Post, **post_data, id_writer = writer.id)
        
        data_comments = data.get('comments')
        for comment in data_comments:
            c = models.Comment(**comment, id_post = post.id)
            session.add(c)        
        
        post.tags.extend(tags)
        session.add(post)        
       
        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()    




