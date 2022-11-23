from .base import Base
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy import TIMESTAMP, Column, BigInteger, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import func
from .utils import gc_distance


class BookHub(Base):
    __tablename__ = "book_hub"

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(VARCHAR(), nullable=False)
    contacts = Column(VARCHAR(256), nullable=True)
    country = Column(VARCHAR(256), nullable=True)
    city = Column(VARCHAR(256), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    registrated_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )

    @hybrid_method
    def calculate_distance(self, location: tuple):
        res = gc_distance((float(self.latitude), float(self.longitude)), location)
        return res

    @calculate_distance.expression
    def calculate_distance(cls, location: tuple):
        res = gc_distance(
            (cls.latitude.cast(Float), cls.longitude.cast(Float)), location, math=func
        )
        return res
