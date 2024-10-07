from flask import Flask, render_template, request, jsonify
import pywhatkit
from datetime import datetime
import re
import time
import pyautogui
import webbrowser
from threading import Timer
import keyboard

app = Flask(__name__)

def close_tab():
    keyboard.press_and_release('ctrl+w')

def send_whatsapp_message(phone, message, hour, minute):
    try:
        # Calculate time difference in seconds
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        time_diff = (target_time - now).total_seconds()
        
        if time_diff <= 0:
            # If the time has already passed or it's for now, send instantly
            pywhatkit.sendwhatmsg_instantly(
                phone, 
                message,
                wait_time=45,  # Increased default wait time
                tab_close=True,
                close_time=5  # Close tab after 5 seconds
            )
        else:
            # Schedule for future
            pywhatkit.sendwhatmsg(
                phone, 
                message, 
                hour, 
                minute, 
                wait_time=45,  # Increased default wait time
                tab_close=True,
                close_time=5  # Close tab after 5 seconds
            )
        return True, "Message scheduled successfully"
    except Exception as e:
        return False, str(e)

def validate_phone_number(phone):
    # Remove any spaces or special characters
    phone = re.sub(r'[^0-9+]', '', phone)
    
    # Check if the number starts with + and has 12-13 digits total
    if phone.startswith('+') and 12 <= len(phone) <= 13:
        return phone
    # If number doesn't start with +, add +91 (India code)
    elif len(phone) == 10:
        return f"+91{phone}"
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_message():
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        hour = int(data.get('hour'))
        minute = int(data.get('minute'))

        # Validate phone number
        validated_phone = validate_phone_number(phone)
        if not validated_phone:
            return jsonify({'error': 'Invalid phone number format'}), 400

        # Validate time
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return jsonify({'error': 'Invalid time format'}), 400

        # Validate message
        if not message or len(message.strip()) == 0:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Send or schedule message
        success, message_response = send_whatsapp_message(validated_phone, message, hour, minute)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Message scheduled for {hour:02d}:{minute:02d}'
            })
        else:
            return jsonify({'error': message_response}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
if __name__ == '__main__':
    # Disable pywhatkit log file creation
    pywhatkit.log_file_location = None
    app.run(debug=True)