from app import db
from models import User, Event, Booking

# Create the database and the tables
db.create_all()

# Add sample events (optional)
event1 = Event(name='Concert', tickets_available=100)
event2 = Event(name='Movie Premiere', tickets_available=50)
db.session.add_all([event1, event2])
db.session.commit()

print("Database initialized!")
