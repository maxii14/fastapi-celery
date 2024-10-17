from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, insert
from sqlalchemy.engine.base import Connection
from config import settings

engine = create_engine(url=settings.get_db_url(), echo=True)
metadata = MetaData()

serial_numbers = Table(
    "serial_numbers",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("code_model", String, nullable=False),
    Column("sn_number", Integer, nullable=False),
    Column("serial_number", String, nullable=False)
)

# Создаём таблицы, если их нет
metadata.create_all(engine)

def insert_new_sn(values: list, connection: Connection):
    ins = insert(serial_numbers).values(values)
    connection.execute(ins)
