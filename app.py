from flask import Flask, request, flash, jsonify, render_template, redirect, url_for
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)

HOST_BASE_URL = "http://pay.mcrh.or.ke/"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def get_access_token():
	consumer_key = "rmvIvMoWnUkcLGPyHGGUgwPof9mtdhe0"
	consumer_secret = "blFXrIhzJphHQY5T"
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

@app.route("/pay", methods=["GET", "POST"])
def initiate_payment():
	message = None
	if request.method == "POST":
		# stk push(Lipa na Mpesa Online)
		customer_phone = request.form.get("customer-phone")
		amount = request.form.get("amount")

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
		    "CallBackURL": HOST_BASE_URL + "/mpesa_express",
		    "AccountReference": "AzoCionXYZ",
		    "TransactionDesc": "Payment of X" 
		  }

		base_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

		response = requests.post(base_url, headers=headers,json = payload)

		try:
			error = response.json()["errorMessage"]
			message = error + ", error occurred when trying to initiate payment"
		except KeyError:
			message = "Payment initiated successfully"
		flash(message)
		return redirect(url_for('initiate_payment'))

	return render_template("pay.html", confirm_message=message)

@app.route("/register-urls")
def register_urls():
	base_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
	headers = {
	  'Content-Type': 'application/json',
	  'Authorization': 'Bearer {}'.format(get_access_token())
	}

	payload = {
	    "ShortCode": 600983,
	    "ResponseType": "Completed",
	    "ConfirmationURL": HOST_BASE_URL + "/confirm-transaction",
	    "ValidationURL": HOST_BASE_URL + "/validate-transaction",
	  }

	response = requests.post(base_url, headers = headers, data = payload)

	return jsonify(response.json())

@app.route("/confirm-transaction", methods=["POST"])
def transaction_confirmation():
	response_data = request.get_json()
	print(response_data)
	return "New transaction confirmed"


@app.route("/validate-transaction", methods=["POST"])
def validate_transaction():
	response_data = request.get_json()
	amount_due = 100
	print(response_data)
	if int(response_data["TransAmount"]) == amount_due:
		validation_response = {"ResultCode": 0, "ResultDesc": "Accepted"}
	else:
		validation_response = {"ResultCode": "C2B00013", "ResultDesc": "Rejected"}

	return jsonify(validation_response)


@app.route("/simulate-pay")
def simulate_c2b_transaction():
	pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5500", debug=True)