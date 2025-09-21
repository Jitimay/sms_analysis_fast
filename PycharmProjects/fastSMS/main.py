# Save this code as app.py
import os
import requests
from flask import Flask, request, jsonify

# --- Configuration ---
# It's best practice to get your API key from an environment variable
# instead of hardcoding it in the script.
# Correctly assign the key as a string
OPENROUTER_API_KEY = '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'
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# You can change the model here. 
# Find more models at: https://openrouter.ai/models
# For a fast and capable free model, google/gemini-flash-1.5 is a great choice.
AI_MODEL = "deepseek/deepseek-chat-v3.1:free"

# Initialize the Flask application
app = Flask(__name__)


@app.route('/ask', methods=['POST'])
def handle_ask():
    """
    This is the main endpoint that the ESP32 will contact.
    It expects a JSON payload like: {"message": "Your question here"}
    """
    print("--- Received a new request ---")

    # 1. Check if the API Key is configured on the server
    if not OPENROUTER_API_KEY:
        print("🔴 ERROR: OPENROUTER_API_KEY environment variable not set.")
        # Return a 500 Internal Server Error
        return jsonify({"error": "Server is not configured with an API key."}), 500

    # 2. Get the JSON data from the ESP32's request
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            print("🔴 ERROR: Invalid JSON or missing 'message' key.")
            # Return a 400 Bad Request error
            return jsonify({"error": "Missing 'message' key in request JSON."}), 400
    except Exception as e:
        print(f"🔴 ERROR: Could not parse request body as JSON. Error: {e}")
        return jsonify({"error": "Invalid JSON format."}), 400

    prompt = data['message']
    print(f"✅ Received prompt: '{prompt}'")

    # 3. Prepare the request to send to the OpenRouter AI API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    # 4. Send the request and handle the response
    try:
        print(f"➡️  Forwarding request to OpenRouter for model: {AI_MODEL}...")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=25)  # 25-second timeout

        # Check if the request to OpenRouter was successful
        response.raise_for_status()  # This will raise an exception for HTTP error codes (4xx or 5xx)

        ai_response_data = response.json()

        # Extract the actual text reply from the AI's response structure
        ai_reply = ai_response_data['choices'][0]['message']['content']
        print(f"⬅️  Received AI reply: '{ai_reply}'")

        # 5. Send the successful reply back to the ESP32
        return jsonify({"reply": ai_reply})

    except requests.exceptions.RequestException as e:
        # Handle network errors (timeout, connection error, etc.)
        print(f"🔴 NETWORK ERROR contacting OpenRouter: {e}")
        return jsonify({"error": "Could not connect to the AI service."}), 503  # Service Unavailable

    except (KeyError, IndexError) as e:
        # Handle cases where the AI response format is unexpected
        print(f"🔴 PARSING ERROR: Could not extract reply from AI response. Error: {e}")
        return jsonify({"error": "Invalid response format from AI service."}), 500

    except Exception as e:
        # Handle all other potential errors (e.g., from raise_for_status)
        print(f"🔴 UNEXPECTED ERROR: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500


# --- This part runs the server ---
if __name__ == '__main__':
    # 'host="0.0.0.0"' makes the server accessible from other devices on your network (like your ESP32)
    # 'port=5000' matches the port in your ESP32 code
    print("🚀 Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)