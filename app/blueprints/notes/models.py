import datetime

from app.orm.orm import SimpleORM


class Note(SimpleORM):
    __tablename__ = "notes"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    title: str
    content: str
