from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# KHÔNG gắn schema tại đây → để rỗng và dùng search_path ở session
Base = declarative_base(metadata=MetaData())