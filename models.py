from orm import SimpleORM


class Note(SimpleORM):
    __tablename__ = "notes"
    title: str
    content: str