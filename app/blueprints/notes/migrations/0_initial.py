from app.blueprints.notes.models import Note


def forward():
    Note.create_table()


# def reverse():
#     Note.drop_table()
