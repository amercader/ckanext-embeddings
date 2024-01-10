
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, types, Column

from pgvector.sqlalchemy import Vector
from ckan import model

from ckan.plugins import toolkit


class DatasetEmbedding(toolkit.BaseModel):

    __tablename__ = "embeddings"

    package_id = Column(
        types.UnicodeText, ForeignKey(model.Package.id), primary_key=True
    )
    updated = Column(types.DateTime, default=datetime.utcnow)
    # TODO parametrize

    embedding = Column("embedding", Vector(384))
    #embedding = Column("embedding_openai", Vector(1536))
    #embedding = Column("embedding_st_multilingual", Vector(512))
