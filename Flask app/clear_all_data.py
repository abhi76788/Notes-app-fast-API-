from website.models import Base, engine, SessionLocal, User, Note

if __name__ == "__main__":
    print("Deleting all users and notes...")
    session = SessionLocal()
    session.query(Note).delete()
    session.query(User).delete()
    session.commit()
    session.close()
    print("All user and note data cleared.")
