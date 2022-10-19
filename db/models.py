from db.database import Base
from sqlalchemy import TIMESTAMP, Column, Numeric, BigInteger, Integer, String, Boolean, text


class BookHub(Base):
    __tablename__ = "book_hub"

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    contacts = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    registrated_at = Column(TIMESTAMP(timezone=True),
                            server_default=text('now()'), nullable=False)
