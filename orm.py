import uuid
import psycopg2.extras

# call it in any place of your program
# before working with UUID objects in PostgreSQL
psycopg2.extras.register_uuid()

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import List, Optional, Type, TypeVar

T = TypeVar('T', bound='BaseModel')


class SimpleORM(BaseModel):
    id: Optional[uuid.UUID] = None

    @classmethod
    def from_db(cls: Type[T], data: dict) -> T:
        print(data)
        return cls(**data)

    @classmethod
    def get(cls: Type[T], conn, id: uuid.uuid4) -> Optional[T]:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {cls.__tablename__} WHERE id = %s", (id,))
            row = cur.fetchone()
            return cls.from_db(row) if row else None

    @classmethod
    def all(cls: Type[T], conn) -> List[T]:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {cls.__tablename__}")
            rows = cur.fetchall()
            return [cls.from_db(row) for row in rows]

    def save(self, conn) -> None:
        with conn.cursor() as cur:
            if self.id is None:
                self.id = uuid.uuid4()
                # Inserting new record
                insert_sql_query = f"INSERT INTO {self.__tablename__} ({', '.join(self.dict().keys())}) VALUES ({', '.join(['%s'] * len(self.dict()))}) RETURNING id"
                print(insert_sql_query)
                cur.execute(
                    insert_sql_query,
                    tuple(self.dict().values())
                )
                self.id = cur.fetchone()[0]  # get the auto-generated id
            else:
                # Updating existing record
                cur.execute(
                    f"UPDATE {self.__tablename__} SET "
                    f"{', '.join([f'{k} = %s' for k in self.dict().keys() if k != 'id'])} "
                    f"WHERE id = %s",
                    (*[v for k, v in self.dict().items() if k != 'id'], self.id)
                )
            conn.commit()

    @classmethod
    def create_table(cls, conn) -> None:
        with conn.cursor() as cur:
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {cls.__tablename__} (
                id UUID PRIMARY KEY,
                {', '.join([f"{name} TEXT" for name in cls.__annotations__ if name != 'id'])}
            )
            """)
            conn.commit()

    def delete(self, conn) -> None:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.__tablename__} WHERE id = %s", (self.id,))
            conn.commit()


class Note(SimpleORM):
    __tablename__ = 'notes'
    title: str
    content: str
