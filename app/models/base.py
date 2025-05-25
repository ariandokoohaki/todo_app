from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer

Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
