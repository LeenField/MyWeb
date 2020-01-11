from watchlist import db,models

from watchlist.models import Article, Tag
a1 = db.session.query(Article).first()
t3 = Tag(id_tag=3, tag_name="影评")
db.session.add(t3)
try:
    db.session.commit()
except:
    db.session.rollback()
#  db.session.flush()

try:    
    a1.tags.append("影评")
except:
    db.session.rollback()
t = 1
# def _keyword_find_or_create(kw):      
#     keyword = Keyword.query.filter_by(keyword=kw).first()     
#     if not(keyword):                    
#         keyword = Keyword(keyword=kw)         # if aufoflush=False used in the session, then uncomment below         
#         #session.add(keyword)         
#         # #session.flush()     
#         return keyword 
# class User(Base):     
#     __tablename__ = 'user'     
#     id = Column(Integer, primary_key=True)     
#     name = Column(String(64))     
#     kw = relationship("Keyword", secondary=lambda: userkeywords_table)     
#     keywords = association_proxy('kw', 'keyword', creator=_keyword_find_or_create)       # @note: this is the )
# 另外一种
# from sqlalchemy import event  # Same User and Keyword classes from documentation  
# class UserKeyword(Base):     
#     __tablename__ = 'user_keywords'      # Columns     
#     user_id = Column(Integer, ForeignKey(User.id), primary_key=True)     
#     keyword_id = Column(Integer, ForeignKey(Keyword.id), primary_key=True)     
#     special_key = Column(String(50))      # Bidirectional attribute/collection of 'user'/'user_keywords'     
#     user = relationship(User, backref=backref('user_keywords' ,cascade='all, delete-orphan'))      
#     # Reference to the 'Keyword' object     
#     keyword = relationship(Keyword)      
#     def __init__(self, keyword=None, user=None, special_key=None):         
#         self._keyword_keyword = keyword_keyword  # temporary, will turn into a                                                  
#         # Keyword when we attach to a                                                   
#         # # Session         
#         self.special_key = special_key      @property     
#     def keyword_keyword(self):         
#         if self.keyword is not None:             
#             return self.keyword.keyword         
#             else:             
#                 return self._keyword_keyword      
        
#                 @event.listens_for(Session, "after_attach")     
#         def after_attach(session, instance):         # when UserKeyword objects are attached to a Session, figure out what          # Keyword in the database it should point to, or create a new one         if isinstance(instance, UserKeyword):             with session.no_autoflush:                 keyword = session.query(Keyword).\                     filter_by(keyword=instance._keyword_keyword).\                     first()                 if keyword is None:                     keyword = Keyword(keyword=instance._keyword_keyword)                 instance.keyword = keyword 