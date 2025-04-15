import requests
import json

class LineMessagingApi:
    """
    Class for sending messages using LINE Messaging API
    """
    
    def __init__(self, channel_token, user_id):
        """
        Initialize
        
        Args:
            channel_token: LINE Messaging API channel access token
            user_id: User ID to send messages to
        """
        self.channel_token = channel_token
        self.user_id = user_id
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {channel_token}"
        }
    
    def send_text_message(self, text):
        """
        Send text message
        
        Args:
            text: Text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/message/push"
        
        data = {
            "to": self.user_id,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error sending message: {response.status_code} {response.text}")
            return False
    
    def send_analysis_report(self, summary_data):
        """
        Send analysis report
        
        Args:
            summary_data: Analysis summary data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Separate buy and sell signals
        buy_signals = [item for item in summary_data if item["signal"] == "BUY"]
        sell_signals = [item for item in summary_data if item["signal"] == "SELL"]
        
        # Count buy and sell signals
        buy_count = len(buy_signals)
        sell_count = len(sell_signals)
        hold_count = len(summary_data) - buy_count - sell_count
        
        # Determine market trend
        if buy_count > sell_count:
            market_trend = "Uptrend is dominant"
        elif sell_count > buy_count:
            market_trend = "Downtrend is dominant"
        else:
            market_trend = "Market is balanced"
        
        # Create message
        message = f"Cryptocurrency Swing Trading Analysis Results\n\n"
        message += f"Market Trend: {market_trend}\n"
        message += f"Buy Signals: {buy_count} coins\n"
        message += f"Sell Signals: {sell_count} coins\n"
        message += f"Hold: {hold_count} coins\n\n"
        
        # Top 3 buy signals
        if buy_signals:
            message += "【Recommended Buy Coins】\n"
            for i, item in enumerate(sorted(buy_signals, key=lambda x: x["confidence"], reverse=True)[:3]):
                message += f"{i+1}. {item['coin']}: ${item['price']:.4f} (Confidence: {item['confidence']:.1f}%)\n"
                message += f"   Entry: ${item['entry_point']:.4f}, Exit: ${item['exit_point']:.4f}\n"
            message += "\n"
        
        # Top 3 sell signals
        if sell_signals:
            message += "【Recommended Sell Coins】\n"
            for i, item in enumerate(sorted(sell_signals, key=lambda x: x["confidence"], reverse=True)[:3]):
                message += f"{i+1}. {item['coin']}: ${item['price']:.4f} (Confidence: {item['confidence']:.1f}%)\n"
                message += f"   Entry: ${item['entry_point']:.4f}, Exit: ${item['exit_point']:.4f}\n"
            message += "\n"
        
        # Send
        return self.send_text_message(message)
    
    def send_image(self, image_url):
        """
        Send image message
        
        Args:
            image_url: URL of the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/message/push"
        
        data = {
            "to": self.user_id,
            "messages": [
                {
                    "type": "image",
                    "originalContentUrl": image_url,
                    "previewImageUrl": image_url
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error sending image: {response.status_code} {response.text}")
            return False