import asyncio
import os
from dotenv import load_dotenv
from notificationapi_python_server_sdk import notificationapi
from pymongo import MongoClient
import certifi
import urllib.request
import json

load_dotenv()

# Use credentials from .env file    
notificationapi.init(
  os.getenv("NOTIFICATIONAPI_CLIENT_ID"), 
  os.getenv("NOTIFICATIONAPI_CLIENT_SECRET")
)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "crime_dashboard")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "users")

def get_latest_crime():
    url = "https://phl.carto.com/api/v2/sql?q=SELECT+text_general_code,location_block+FROM+incidents_part1_part2+ORDER+BY+dispatch_date+DESC,dispatch_time+DESC+LIMIT+1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and "rows" in data and len(data["rows"]) > 0:
                row = data["rows"][0]
                return {
                    "type": row.get("text_general_code", "Unknown Crime"),
                    "location": row.get("location_block", "Unknown Location")
                }
    except Exception as e:
        print(f"Error fetching crime data: {e}")
    
    return {"type": "Unknown Crime", "location": "Unknown Location"}

async def send_notification():
    latest_crime = get_latest_crime()
    crime_type = latest_crime["type"]
    crime_location = latest_crime["location"]

    if not MONGO_URI or MONGO_URI == "mongodb+srv://mailemail761_db_user:[EMAIL_ADDRESS]/?retryWrites=true&w=majority":
        print("Please configure your MONGO_URI in the .env file")
        return

    try:
        # certifi.where() ensures secure connections to Atlas on all OSes
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client[MONGO_DB_NAME]
        users_collection = db[MONGO_COLLECTION_NAME]

        # Fetch all users from the collection
        users = users_collection.find({})
        
        count = 0
        for user in users:
            # Check user preferences
            prefs = user.get("preferences", {})
            email_enabled = prefs.get("email_enabled", True) # Default true if missing
            sms_enabled = prefs.get("sms_enabled", False); # Default false if missing
            
            user_id = str(user.get("_id"))
            email = user.get("email")
            phone = user.get("phone") or user.get("number") # fallback
            
            if not email or (not email_enabled and not sms_enabled):
                continue # Skip if no email or all notifications are disabled
                
            try:
                # Build the notification payload dynamically based on preferences
                payload = {
                  "notificationId": "crime_dashboard",
                  "user": {
                     "id": user_id, 
                     "email": email,
                     "number": phone if phone else ""
                  }
                }
                
                if email_enabled:
                    payload["email"] = {
                        "subject": f"Crime Alert: {crime_type}",
                        "html": f"<b>A {crime_type} has been reported near {crime_location}.</b>"
                    }
                    
                if sms_enabled and phone:
                    payload["sms"] = {
                        "message": f"Crime Alert: A {crime_type} has been reported near {crime_location}. Check your dashboard."
                    }
                    
                # Always send inapp if they log into the dashboard
                payload["inapp"] = {
                    "title": f"New Crime Alert: {crime_type}",
                    "body": f"Reported near {crime_location}. Click here to view the dashboard.",
                    "url": "http://localhost:3000/index.html"
                }

                await notificationapi.send(payload)
                count += 1
                print(f"Sent notification to {email} (Email: {email_enabled}, SMS: {sms_enabled and bool(phone)})")
            except Exception as e:
                print(f"Failed to send to {email}: {e}")
                
        print(f"Notification run complete! Sent alerts to {count} users.")
    except Exception as e:
        print(f"Error checking MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(send_notification())