from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)

def get_access_token():
	consumer_key = None
	consumer_secret = None
	base_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
	response = requests.get(base_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

	data = json.loads(response.text)

	try:
		return data["access_token"]
	except:
		return data

@app.route("/")
def home():
	return "Welcome, this is the home page"	

@app.route("/auth")
def auth():
	return get_access_token()

@app.route("/mpesa_express", methods=["POST"])
def stk_push():
	response_data = request.get_json()
	json_file = open("stk_push_results.json", "a")
	response_data = json.dumps(response_data)
	json_file.writelines(response_data+"\n")
	json_file.close()
	print(response_data)
	return "STK push complete"

@app.route("/pay")
def initiate_payment():
	# stk push(Lipa na Mpesa Online)
	customer_phone = request.args.get("customer-phone")
	amount = request.args.get("amount")

	headers = {
	  'Content-Type': 'application/json',
	  'Authorization': 'Bearer {}'.format(get_access_token())
	}

	payload = {
	    "BusinessShortCode": 174379,
	    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjMwMzE1MTE1NDAz",
	    "Timestamp": "20230315115403",
	    "TransactionType": "CustomerPayBillOnline",
	    "Amount": amount,
	    "PartyA": customer_phone,
	    "PartyB": 174379,
	    "PhoneNumber": customer_phone,
	    "CallBackURL": "https://3664-212-22-184-178.in.ngrok.io/mpesa_express",
	    "AccountReference": "AzoCionXYZ",
	    "TransactionDesc": "Payment of X" 
	  }

	base_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

	response = requests.post(base_url, headers=headers,json = payload)

	return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5500", debug=True)