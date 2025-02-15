import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy import  Column, String, Integer, LargeBinary, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from models import User, Location,State,TravelData,Tag, UserTags
from main import engine  
import uvicorn
from typing import List

# FastAPI app setup
app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allows all origins; in production, specify allowed origins like ["http://127.0.0.1:64837"]
    allow_credentials=True,       # Allows cookies and authentication headers to be sent in requests
    allow_methods=["*"],          # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allows all HTTP headers
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Pydantic models for data validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    location: str
    state: str
    country: str


   
class UserResponse(BaseModel):
    username_id: int
    username: str
    email: str
    location :str
    state: str
    country : str
    password:str
    
class UserR(BaseModel):
    username_id: int
    username: str
    email: str
    profie_pic:str
    location_id: int
    crptkey: str

class Travel(BaseModel):
    username_id: int
    username: str
    start_location: str
    start_location_state: str
    start_location_country: str

    destination: str
    destination_state: str
    destination_country: str
    travel_date: str
    travel_type: str
    travel_price: int
    days: int
    stay: bool
    stay_price: int
    travel_time: int
    fromdate: datetime.date
    todate: datetime.date
    backdate: datetime.date
    #
class Travel_db(BaseModel):
    username_id: int
    start_location_id: int
    
    destination_id: int

    travel_type: str
    travel_price: int
    days: int
    stay: bool
    stay_price: int
    travel_time: int
    fromdate: datetime.date
    todate: datetime.date
    backdate: datetime.date
    


    class Config:
        from_attribute = True

class location(BaseModel):

    Location_name: str
    State_name: str
    Country_name: str
class location_db(BaseModel):
    location_id: int
    location_name: str
    state_id: int
    state_name: str
    country_name: str
    class Config:
        from_attribute = True

class UserTagsInput(BaseModel):
    username: str
    tags: List[str]


class TagOut(BaseModel):
    tags_id: int
    tag: str

    class Config:
        orm_mode = True
        
# Dependency to get the database session
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# FastAPI Routes
@app.post("/location/")
async def location(location: location, db: Session = Depends(get_db)): #for entering location directly
   existing_location = db.query(Location).filter(Location.location_name == location.Location_name).first()
   State_name = state_add(state=location.State_name, country=location.Country_name, db=db)
   new_location = Location(
         location_name=location.Location_name,
            state_id=State_name.state_id
    )

   db.add(new_location)
   db.commit()
   db.refresh(new_location)
    
def state_add(state: str, country: str, db: Session = Depends(get_db)):
    existing_country = db.query(State).filter(State.country_name == country).first()
    if not existing_country:
        new_country = State(
            new_state=state,
            country_name=country
        )
        db.add(new_country)
        db.commit()
        db.refresh(new_country)
        existing_country = new_country
        return  existing_country
    
    elif    existing_country:
        existing_state = db.query(State).filter(State.state_name == state).first()
        if not existing_state:
            new_state = State(
                state_name=state,
                country_name=country,
        
            )
            db.add(new_state)
            db.commit()
            db.refresh(new_state)
            existing_state = new_state
            return existing_state
        else:
            return existing_state





@app.post("/register/") #, response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)): #for registering user
    print(locals())
    # Check if the user or email already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        print('existing_user')
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_location = location_add(country=user.country,state=user.state,location=user.location,db=db)
    
    
    # Hash the password before storing
    hashed_password = hash_password(user.password)
   # Create the user record in the database
    
    
    new_user = User(
        username=user.username,
        email=user.email,
        cryptkey=hashed_password,
        location_id=existing_location.location_id
       
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user




# FastAPI Routes 
@app.post("/travel/")  # , response_model=UserResponse)  
async def travel(travel: Travel, db: Session = Depends(get_db)): #for entering there data into the table
    print(locals())
    # Check if the user or email already exists
    existing_user = db.query(User).filter(User.username_id == travel.username_id).first()
    start_location = location_add(location=travel.start_location, state=travel.start_location_state,country= travel.start_location_country, db=db)
    destination = location_add(location=travel.destination, state=travel.destination_state, country=travel.destination_country, db=db)
    new_Travel_data= TravelData(
        username_id=travel.username_id,
        start_location=start_location.location_id,
        destination=destination.location_id,
        travel_type=travel.travel_type,
        travel_price=travel.travel_price,
        days=travel.days,
        stay=travel.stay,
        stay_price=travel.stay_price,
        travel_time=travel.travel_time,
        fromdate=travel.fromdate,
        todate=travel.todate,
        backdate=travel.backdate
    )
    db.add(new_Travel_data)
    db.commit()
    db.refresh(new_Travel_data)
    


    return destination

def location_add(country: str, state: str, location: str, db: Session = Depends(get_db)):
    existing_country = db.query(State).filter(State.country_name == country).first()
    if existing_country:
        print('existing_state')
    
    existing_state = db.query(State).filter(State.state_name == state).first()
    if not existing_state:
        new_state = State(
            state_name=state,
            country_name=country,
        
        )
        db.add(new_state)
        db.commit()
        db.refresh(new_state)
        existing_state = new_state
    
    existing_location = db.query(Location).filter(Location.location_name == location).first()
    if not existing_location:
        new_location = Location(
            location_name=location,
            state_id=existing_state.state_id
        )
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
        existing_location = new_location
    
    
    else:
        print('existing_state')
    print(existing_location.location_id)
    return existing_location




@app.get("/user/{username}")
async def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@app.get("/travel_data/{user_id}")
async def travel_data(user_id: int, db: Session = Depends(get_db)):
    # to output the entire histroy of the user!
    travel_info = db.query(TravelData).filter(TravelData.username_id == user_id).all() 
    
    import json
    
    # Convert the list of ORM objects to a list of dictionaries
    travel_info_json = [
        {
            "id": record.table_id,
            "username_id": record.username_id,
            "start_location": record.start_location,
            "destination": record.destination,
            "travel_type": record.travel_type,
            "travel_price": record.travel_price,
            "days": record.days,
            "stay": record.stay,
            "stay_price": record.stay_price,
            "travel_time": record.travel_time,
            "fromdate": record.fromdate.isoformat() if record.fromdate else None,
            "todate": record.todate.isoformat() if record.todate else None,
            "backdate": record.backdate.isoformat() if record.backdate else None
        }
        for record in travel_info
    ]
    
    # Serialize to JSON
    travel_info_json_str = json.dumps(travel_info_json)
    
    print(travel_info_json_str)
    
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    return travel_info_json_str




@app.get("/location/{location_id}")
async def get_location(location_id: int, db: Session = Depends(get_db)):
    # Retrieve the location record from the database.
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Retrieve the state details using the location's state_id.
    state_record = db.query(State).filter(State.state_id == location.state_id).first()
    
    # Build the response dictionary with the location info.
    response_data = {
         "location_id": location.location_id,
         "location_name": location.location_name,
         "state_id": location.state_id,
    }
    
    # If state information exists, add the state name and country name.
    if state_record:
         # Use the appropriate attribute names; adjust if your model uses different names.
         response_data["state_name"] = state_record.state_name
         response_data["country_name"] = state_record.country_name
    
    return response_data


@app.get("/passcheck/{username}/{password}")
#checks the password of the user sign in procces
async def get_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user.cryptkey):
        raise HTTPException(status_code=401, detail="Invalid password")
    return user.username



@app.get("/user/{password_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(username=user.username, password=user.password)


@app.put("/user/{user_id}/profile", response_model=UserResponse)
async def update_profile_pic(user_id: int, profile_pic: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # still untested will work on it if i have time!!! 
    profile_pic_data = await profile_pic.read()
    user.profile_pic = profile_pic_data
    db.commit()
    db.refresh(user)
    
    return user

@app.get("/user/{user_id}/profile")
async def get_profile_pic(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
   
    # Return the profile picture as a binary response
    if user.profile_pic:
        from fastapi.openapi.models import Response
        return Response(content=user.profile_pic, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Profile picture not found")
#probably will remian like that for a long time!!!!


@app.post("/user/tags")
async def add_user_tags(user_tags_input: UserTagsInput, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.username == user_tags_input.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    added_tags = []
    
    # Iterate over each tag provided from the frontend
    for tag_str in user_tags_input.tags:
        # Check if the tag already exists in the Tag table
        tag = db.query(Tag).filter(Tag.tag == tag_str).first()
        if not tag:
            # If the tag does not exist, create a new Tag record
            tag = Tag(tag=tag_str)
            db.add(tag)
            db.commit()  # Commit so the tag gets an ID
            db.refresh(tag)
        
        # Check if the user already has this tag associated
        association = (
            db.query(UserTags)
            .filter(UserTags.username_id == user.username_id, UserTags.tags_id == tag.tags_id)
            .first()
        )
        
        if not association:
            # Create the association between the user and the tag
            user_tag_assoc = UserTags(username_id=user.username_id, tags_id=tag.tags_id)
            db.add(user_tag_assoc)
            added_tags.append(tag_str)
    
    db.commit()  # Commit all associations
    
    return {"message": "Tags added successfully", "added_tags": added_tags}

@app.get("/user/{username}/tags", response_model=List[TagOut])
async def get_user_tags(username: str, db: Session = Depends(get_db)):
    # Query the user by username.
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the list of tags associated with the user.
    # The relationship "tags" should be defined in the User model (using secondary=UserTags).
    return user.tags
#
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5003)
# """