from Backend.app.core.database import engine
from Backend.app.models.user import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')