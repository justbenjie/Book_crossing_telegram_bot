from db.base import Base
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, VARCHAR
from sqlalchemy import TIMESTAMP, Column, BigInteger, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from geopy import distance as dis

class BookHub(Base):
    __tablename__ = "book_hub"

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(VARCHAR(256), nullable=False)
    contacts = Column(VARCHAR(256), nullable=True)
    country = Column(VARCHAR(256), nullable=True)
    city = Column(VARCHAR(256), nullable=True)
    latitude = Column(DOUBLE_PRECISION, nullable=False)
    longitude = Column(DOUBLE_PRECISION, nullable=False)
    registrated_at = Column(TIMESTAMP(timezone=True),
                            server_default=text('now()'), nullable=False)

    @hybrid_method
    def calculate_distance(self, location: tuple, distance: float):
        res = dis.distance((float(self.latitude), float(self.longitude)), location).kilometers
        return res


    @calculate_distance.expression
    def calculate_distance(cls, location: tuple, distance: float):
        res = dis.distance((cls.latitude.cast(Float), cls.longitude.cast(Float)), location).kilometers
        return res

