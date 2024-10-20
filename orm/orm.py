import uuid
from contextlib import contextmanager
import datetime

import psycopg2.extras

from app.config import settings

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import List, Optional, Type, TypeVar

from utils import setup_logger

psycopg2.extras.register_uuid()

T = TypeVar("T", bound="BaseModel")

logger = setup_logger(__name__)


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        yield conn
    except Exception as e:
        logger.error(e)
        raise
    finally:
        if conn:
            logger.debug("Closing connection.")
            conn.close()


class SimpleORM(BaseModel):
    id: Optional[uuid.UUID] = None

    @classmethod
    def from_db(cls: Type[T], data: dict) -> T:
        return cls(**data)

    @classmethod
    def get(cls: Type[T], id: uuid.uuid4) -> Optional[T]:
        with get_db_connection() as conn, conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:
            cur.execute(f"SELECT * FROM {cls.__tablename__} WHERE id = %s", (id,))
            row = cur.fetchone()
            return cls.from_db(row) if row else None

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        with get_db_connection() as conn, conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:
            cur.execute(f"SELECT * FROM {cls.__tablename__}")
            rows = cur.fetchall()
            return [cls.from_db(row) for row in rows]

    def save(self) -> None:
        with get_db_connection() as conn, conn.cursor() as cur:
            if self.id is None:
                self.id = uuid.uuid4()
                insert_sql_query = f"INSERT INTO {self.__tablename__} ({', '.join(self.model_dump().keys())}) VALUES ({', '.join(['%s'] * len(self.model_dump()))}) RETURNING id"
                cur.execute(insert_sql_query, tuple(self.model_dump().values()))
                self.id = cur.fetchone()[0]
            else:
                cur.execute(
                    f"UPDATE {self.__tablename__} SET "
                    f"{', '.join([f'{k} = %s' for k in self.model_dump().keys() if k != 'id'])} "
                    f"WHERE id = %s",
                    (*[v for k, v in self.model_dump().items() if k != "id"], self.id),
                )
            conn.commit()

    @classmethod
    def _annotation_to_column_type(cls, annotation: type) -> str:
        if annotation is datetime.datetime:
            return "TIMESTAMPTZ"
        elif annotation is str:
            return "TEXT"
        else:
            return "TEXT"

    @classmethod
    def create_table(cls) -> str:
        with get_db_connection() as conn, conn.cursor() as cur:
            columns = {}
            for field_key, field_info in cls.__fields__.items():
                columns.update(
                    {
                        field_key: {
                            "annotation": field_info.annotation,
                            "column_type": cls._annotation_to_column_type(
                                field_info.annotation
                            ),
                        }
                    }
                )
                logger.debug("%s %s", field_key, field_info)

            logger.debug("columns %s", columns)

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {cls.__tablename__} (
                id UUID PRIMARY KEY,
                {', '.join([f"{name} {config.get("column_type")}" for name, config in columns.items() if name != 'id'])}
            )
            """
            logger.debug("create_table_query %s", create_table_query)
            cur.execute(create_table_query)
            conn.commit()

        return create_table_query

    def delete(self) -> None:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.__tablename__} WHERE id = %s", (self.id,))
            conn.commit()
