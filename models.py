from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, BigInteger, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base


#oh yeh this isn't making a new database but rather connecting to an existing one!
#that is this just create python class for the database
# Create the Base class for all models
# in otherwords here we got the base for all the model in the database 
#gpt never mentioned it the first 20000 times
# ahh i see it was outdated by a bit see studying is fun 
#delete the above comments before sumbmitting

Base = declarative_base()

class State(Base):
    __tablename__ = 'state'
    state_id = Column(Integer, primary_key=True)
    state_name = Column(String(255), nullable=False)
    country_name = Column(String(255), nullable=False)

    # Relationship with location and sublocation
    locations = relationship("Location", back_populates="state")
    sublocations = relationship("Sublocation", back_populates="state")


class Location(Base):
    __tablename__ = 'location'
    location_id = Column(Integer, primary_key=True)
    location_name = Column(String(255), nullable=False)
    state_id = Column(Integer, ForeignKey('state.state_id'), nullable=False)

    # Relationship with state
    state = relationship("State", back_populates="locations")

    # Relationship with sublocation and travel data
    sublocations = relationship("Sublocation", back_populates="location")
    start_travel_data = relationship("TravelData", foreign_keys='TravelData.start_location', back_populates="start_location_rel")
    destination_travel_data = relationship("TravelData", foreign_keys='TravelData.destination', back_populates="destination_rel")


class Sublocation(Base):
    __tablename__ = 'sublocation'
    sublocation_id = Column(Integer, primary_key=True)
    sublocation_name = Column(String(255), nullable=False)
    location_id = Column(Integer, ForeignKey('location.location_id'), nullable=False)
    state_id = Column(Integer, ForeignKey('state.state_id'), nullable=False)

    # Relationship with location and state
    location = relationship("Location", back_populates="sublocations")
    state = relationship("State", back_populates="sublocations")


class User(Base):
    __tablename__ = 'username'
    username_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_pic = Column(LargeBinary)
    location_id = Column(Integer, ForeignKey('location.location_id'))
    cryptkey = Column(String)

    # Relationship with location and travel data
    location = relationship("Location")
    travel_data = relationship("TravelData", back_populates="user")
    tags = relationship("Tag", secondary="user_tags")


class TravelData(Base):
    __tablename__ = 'travel_data'
    table_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username_id = Column(BigInteger, ForeignKey('username.username_id'))
    start_location = Column(Integer, ForeignKey('location.location_id'))
    destination = Column(Integer, ForeignKey('location.location_id'))
    fromdate = Column(Date, nullable=False)
    todate = Column(Date, nullable=False)
    backdate = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    travel_type = Column(String(255), nullable=False)
    travel_price = Column(Integer, nullable=False)
    stay_price = Column(Integer)
    stay = Column(Boolean)
    travel_time = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="travel_data")
    start_location_rel = relationship("Location", foreign_keys=[start_location], back_populates="start_travel_data")
    destination_rel = relationship("Location", foreign_keys=[destination], back_populates="destination_travel_data")


class Tag(Base):
    __tablename__ = 'tags'
    tags_id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(255))
    ind_tag_id = Column(Integer, autoincrement=True)
    local_tag = Column(LargeBinary)


class LocationTags(Base):
    __tablename__ = 'location_tags'
    location_id = Column(Integer, ForeignKey('location.location_id'), primary_key=True)
    tags_id = Column(Integer, ForeignKey('tags.tags_id'), primary_key=True)


class SublocationTags(Base):
    __tablename__ = 'sublocation_tags'
    sublocation_id = Column(Integer, ForeignKey('sublocation.sublocation_id'), primary_key=True)
    tags_id = Column(Integer, ForeignKey('tags.tags_id'), primary_key=True)


class UserTags(Base):
    __tablename__ = 'user_tags'
    username_id = Column(BigInteger, ForeignKey('username.username_id'), primary_key=True)
    tags_id = Column(Integer, ForeignKey('tags.tags_id'), primary_key=True)


class UserTravel(Base):
    __tablename__ = 'user_travel'
    username_id = Column(BigInteger, ForeignKey('username.username_id'), primary_key=True)
    table_id = Column(BigInteger, ForeignKey('travel_data.table_id'), primary_key=True)


class Like(Base):
    __tablename__ = 'like'
    like_id = Column(BigInteger, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('location.location_id'), nullable=False)
    upvote = Column(BigInteger)
    downvote = Column(BigInteger)
    totalvote = Column(BigInteger)
