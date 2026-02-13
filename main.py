import os

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/.well-known/agent.json", methods=["GET"])
def agent_card():
  """."""
  return jsonify({
    "name": "Mailer Agent",
    "description": "Draft and Send a Mail",
    "url": "http://127.0.0.1:3000",
    "version": "1.0",
    "capabilites": {
      "streaming": False,
      "pushNotifications": False
    }
  })


@app.route("/task/send", methods=["POST"])
def handle_tasl():
  try:
    print("code",request.get_json())    
  except Exception as e:
    print(e)

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))