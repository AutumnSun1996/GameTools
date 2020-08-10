from sqlalchemy import create_engine, Column, String, Integer, Binary, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Record(Base):
    __tablename__ = "record"
    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String)
    host = Column(String)
    path = Column(String)
    params = Column(String)
    headers = Column(String)
    body = Column(Binary)
    resp_headers = Column(String)
    resp_body = Column(Binary)

    timestamp = Column(DateTime, index=True, default=datetime.datetime.now)


def get_session():
    engine = create_engine('sqlite:///db.sqlite')
    Session = sessionmaker(bind=engine)
    # Session.configure()
    return Session()


if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    Base.metadata.create_all(engine)

    s = get_session()
    rec = Record(
        method="TEST",
        host="TEST",
        path="TEST",
        params="TEST",
        headers="{}",
        body=b"TEST",
        resp_headers="{}",
        resp_body=b"TEST",
    )
    s.add(rec)
    s.flush()
    print(rec.id)
