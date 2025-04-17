import sys
import os
from aws_lambda_deployment.line_messaging_api import LineMessagingApi
import config

def main():
    """Test LINE notification functionality"""
    
    # Get LINE credentials from config
    line_token = config.LINE_CHANNEL_TOKEN
    line_user_id = config.LINE_USER_ID
    
    # Check if credentials are properly set
    placeholder_check = any([
        "YOUR_LINE_CHANNEL_TOKEN" in line_token,
        "あなたの" in line_token,
        "YOUR_LINE_USER_ID" in line_user_id,
        "あなたの" in line_user_id
    ])
    
    if placeholder_check:
        print("Error: Please set your actual LINE credentials in config.py first")
        print("LINE_CHANNEL_TOKEN and LINE_USER_ID need to be set with real values")
        sys.exit(1)
    
    # Initialize LINE client
    line_client = LineMessagingApi(line_token, line_user_id)
    
    # Send test message
    print("Sending test message to LINE...")
    test_message = "🚀 This is a test message from Crypto Analysis System. LINE notification is working properly!"
    
    result = line_client.send_text_message(test_message)
    
    if result:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send message. Please check your LINE credentials.")

if __name__ == "__main__":
    main()