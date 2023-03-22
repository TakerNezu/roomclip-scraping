from app import db
from sqlalchemy import TypeDecorator, BLOB
from sqlalchemy.dialects.mysql import LONGBLOB, LONGBLOB


class LongBinary(TypeDecorator):
    impl = BLOB

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(LONGBLOB())
        else:
            return dialect.type_descriptor(BLOB())


class CacheItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.String(255), primary_key=True)
    data = db.Column(LongBinary(), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
