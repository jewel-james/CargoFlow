import models, database, auth

def create_driver_account():
    db = database.SessionLocal()
    try:
        username = "driver1"
        password = "password123"
        
        # Check if user already exists
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            hashed_pw = auth.get_password_hash(password)
            user = models.User(username=username, password=hashed_pw, role="driver")
            db.add(user)
            db.commit()
            print(f"Created user '{username}' with role 'driver'.")
        
        # Link user to an existing driver profile
        driver = db.query(models.Driver).first()
        if driver:
            driver.user_id = user.id
            db.commit()
            print(f"Linked user '{username}' to driver profile '{driver.name}'.")
        else:
            print("No driver profiles found to link.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_driver_account()
