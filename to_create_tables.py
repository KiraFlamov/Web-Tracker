from database import Base, engine
from models import User, Task

Base.metadata.create_all(bind=engine)
