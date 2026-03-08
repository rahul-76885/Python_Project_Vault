from pydantic import BaseModel, Field, ConfigDict


class POSTBASE(BaseModel):
    author: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=50)


# data schema we get from frontend
class POSTCREATE(POSTBASE):
    pass


# data schema we send to frontend
class POSTRESPONSE(POSTBASE):
    model_config = ConfigDict(from_attributes=True) # some time we have to read from database which we get in form of object and so to read it in form of dict we write this

    id: int
    date_posted: str