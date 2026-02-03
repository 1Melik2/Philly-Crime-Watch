import asyncio
from notificationapi_python_server_sdk import notificationapi


notificationapi.init(
  "m6sulpvh8jxw1f80wgyxa6cp1r", # Client ID
  "55cfjj8p3owjpostwxqqa29jgqqyhh9s1dj62683692hiwyl5xztmws3xa"# Client Secret
)

async def send_notification():
    response = await notificationapi.send({
      "type": "crime_dashboard",
      "to": {
         "id": "mailemail.761@gmail.com",
         "email": "mailemail.761@gmail.com",
         "number": "+15005550006" # Replace with your phone number, use format [+][country code][area code][local number]
      },
        "email": {
            "subject": "Your verification code",
            "html": "Your verification code is: 123456"
        },
        "sms": {
            "message": "Your verification code is: 123456. Reply STOP to opt-out."
        },
        "inapp": {
            "title": "Hello",
            "url": "https://example.com",
            "image": "https://example.com/image.png"
        },
        "call": {
            "message": "This is a test call from NotificationAPI. Your verification code is: 123456"
        }
    })
    