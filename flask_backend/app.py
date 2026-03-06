from flask import Flask, request, jsonify
from notificationapi_python_server_sdk import notificationapi
import asyncio

app = Flask(__name__)

# Initialize NotificationAPI
notificationapi.init(
    "m6sulpvh8jxw1f80wgyxa6cp1r", 
    "55cfjj8p3owjpostwxqqa29jgqqyhh9s1dj62683692hiwyl5xztmws3xa"
)

@app.route('/send-notification', methods=['POST'])
def send_notification_route(): # Renamed to avoid shadowing the 'notificationapi' object
    try:
        notification_payload = {
            "notificationId": "crime_dashboard", # Usually 'notificationId' is used instead of 'type'
            "user": {
               "id": "mailemail.761@gmail.com",
               "email": "mailemail.761@gmail.com",
               "number": "+16104158141" 
            },
            "mergeVariables": { # Use mergeVariables if that's what your template expects
                "comment": "testComment"
            }
        }
        
        # If the SDK is truly async, we run it in a loop:
        asyncio.run(notificationapi.send(notification_payload))
        
        return jsonify({
            "success": True,
            "message": "Notification request processed"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)