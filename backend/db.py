import sqlalchemy
import databases
import ormar

DB = "postgresql://postgres:1234@localhost:5432/mai"
metadata = sqlalchemy.MetaData()
db = databases.Database(DB)
engine = sqlalchemy.create_engine(DB)


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = db