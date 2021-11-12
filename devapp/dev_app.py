#Let's call it device app, this is a controller for devices (iot devices)
from flask import Flask, request,jsonify, Response
import json
from flask_cors import CORS, cross_origin
import hashlib
#for dig significantly
#pip install pycryptodome
from base64 import b64decode
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
import requests


app=Flask(__name__)
CORS(app)


API_ROOT = "/ELL893/muneeb_majid/smarthome/http"
KDC_ADDRESS = "http://127.0.0.1:5000/ELL893/muneeb_majid/smarthome/http/key_fetch"




#Params are some informations about Device App
PARAMS = dict()
PARAMS['DEVICE_APP_IP'] = '127.0.0.1'
PARAMS['DEVICE_APP_PORT'] = '5000'



#DEVICES dictionary contains current devices added/configured to Device App
#Types of devices supported for now:
#1. Ac type (knob for temperature control 0-20, H_Direction: -1 to 1 i.e, left to right)
#2. Fan type (on/off)
#3. SamrtBulb type (contains off/on control, color)



#DEV_IDS= ['smart_bulb1', 'smart_lock1', 'smart_fan1', 'smart_lock1']


PARTIES = ['client1', 'emulator1']

DEVICES = dict()
DEVICE_IDS = ['smart_bulb1', 'smart_lock1', 'smart_fan1','smart_ac1']



#PARAMS_DEVICES = dict()
#PARAMS_DEVICES[DEVICE_IDS[0]] = {'power':'on', 'color':'#FF0000'}
#PARAMS_DEVICES[DEVICE_IDS[1]] = {'power':'on', 'door_status':'close'}
#PARAMS_DEVICES[DEVICE_IDS[2]] = {'power':'on'}
#PARAMS_DEVICES[DEVICE_IDS[3]] = {'power':'on', 'h_direction':'center'}




DEVICES[DEVICE_IDS[0]]= {'device':DEVICE_IDS[0], 'params':{'color':'#000000', 'power':'off'}, 'hash':''}
DEVICES[DEVICE_IDS[1]]= {'device':DEVICE_IDS[1], 'params':{'door_status':'close', 'power':'on'}, 'hash':''}
DEVICES[DEVICE_IDS[2]]= {'device':DEVICE_IDS[2], 'params':{'power':'off'}, 'hash':''}
DEVICES[DEVICE_IDS[3]]= {'device':DEVICE_IDS[3], 'params':{'h_direction':'center', 'power':'off', 'temperature':'10'}, 'hash':''}




def decrypt_this_hash(hash, key):
	decode_data = b64decode(hash)
	other_key = RSA.importKey(b64decode(key))
	cipher = Cipher_PKCS1_v1_5.new(other_key)
	decrypt_text = cipher.decrypt(decode_data, None).decode()
	print(decrypt_text)
	return decrypt_text




@app.route(API_ROOT+"/see_all_devices", methods=['GET'])
#This Handles Default Interface. Does nothing!
def init():
	#for i in range(len(DEVICES.keys())):
	#	dev = list(DEVICES.values())[i]['device']
	#	devices_online.append(dev)
	return "Dev App Loaded. Success!<br> Online Devices: "+ str(list(DEVICES.keys()))


#USER -> COMMAND -> AWS PROCESSING -> DEVAPP (global variable DEVICES,state update)
#EMULATOR-> requests after certain intervals ->Dev apps



@app.route(API_ROOT+"/<devId>", methods=['GET','POST'])
def device_state(devId):	
	#This Handles Device(s) Interface. Handles POST to Device App

	if request.method == 'POST':
		#print(request.json)
		data = json.loads(request.json)

		if not str(devId) in DEVICES.keys():
			message = "no such device found"
			response = jsonify(message=message)
		else:
			#authentication request
			#print(request.json)
			hash_str_received = data.pop('hash', None)
			print(json.dumps(data))

			#Fetching Public Key:	
			public_key = json.loads(requests.get(KDC_ADDRESS+"/client1").text)['public_key']


			hash_str =  decrypt_this_hash(hash_str_received, public_key)
			#hash_str = decrypt_this_hash (hash_str_received)

			#print(request.json)
			hash_computed = hashlib.md5(str(json.dumps(data)).encode('utf-8')).hexdigest()
			#print(hash_computed)
			if not hash_computed == hash_str:
				response= jsonify(message="signature_error")
				response.headers.add("Access-Control-Allow-Origin", "*")
				return response

			#data['hash'] = hash_computed
			if DEVICES[str(devId)]['params'] == data['params']:
				response= jsonify(message="already_updated")
			else:
				DEVICES[str(devId)]['params'].update(data['params'])
				DEVICES[str(devId)]['hash']= hash_str_received   #debug=1 hash_computed
				print(DEVICES[str(devId)])
				response= jsonify(message="success")
			response.headers.add("Access-Control-Allow-Origin", "*")
			return response


	if request.method == 'GET':
		if not str(devId) in DEVICES.keys():
			response = jsonify(message="no_such_device_found")
			response.headers.add("Access-Control-Allow-Origin", "*")
			return response
		else:
			response = jsonify(message=DEVICES[str(devId)])
			response.headers.add("Access-Control-Allow-Origin", "*")
			return response




@app.route(API_ROOT+"/key_fetch/<pId>", methods=['GET'])
def display_keys(pId):
	if str(pId) == "client1":
		with open('./publickey_'+str(pId)+".key", 'r') as f:
			key = f.read()
			response = jsonify(public_key="MIICXQIBAAKBgQDlOJu6TyygqxfWT7eLtGDwajtNFOb9I5XRb6khyfD1Yt3YiCgQWMNW649887VGJiGr/L5i2osbl8C9+WJTeucF+S76xFxdU6jE0NQ+Z+zEdhUTooNRaY5nZiu5PgDB0ED/ZKBUSLKL7eibMxZtMlUDHjm4gwQco1KRMDSmXSMkDwIDAQABAoGAfY9LpnuWK5Bs50UVep5c93SJdUi82u7yMx4iHFMc/Z2hfenfYEzu+57fI4fvxTQ//5DbzRR/XKb8ulNv6+CHyPF31xk7YOBfkGI8qjLoq06V+FyBfDSwL8KbLyeHm7KUZnLNQbk8yGLzB3iYKkRHlmUanQGaNMIJziWOkN+N9dECQQD0ONYRNZeuM8zd8XJTSdcIX4a3gy3GGCJxOzv16XHxD03GW6UNLmfPwenKu+cdrQeaqEixrCejXdAFz/7+BSMpAkEA8EaSOeP5Xr3ZrbiKzi6TGMwHMvC7HdJxaBJbVRfApFrE0/mPwmP5rN7QwjrMY+0+AbXcm8mRQyQ1+IGEembsdwJBAN6az8Rv7QnD/YBvi52POIlRSSIMV7SwWvSK4WSMnGb1ZBbhgdg57DXaspcwHsFV7hByQ5BvMtIduHcT14ECfcECQATeaTgjFnqE/lQ22Rk0eGaYO80cc643BXVGafNfd9fcvwBMnk0iGX0XRsOozVt5AzilpsLBYuApa66NcVHJpCECQQDTjI2AQhFc1yRnCU/YgDnSpJVm1nASoRUnU8Jfm3Ozuku7JUXcVpt08DFSceCEX9unCuMcT72rAQlLpdZir876")
			response.headers.add("Access-Control-Allow-Origin", "*")
			return response
	else:
		response = jsonify(public_key="no_such_party")
		response.headers.add("Access-Control-Allow-Origin", "*")
		return response



if __name__== "__main__":
	app.run(app.run(host=PARAMS['DEVICE_APP_IP'], port=int(PARAMS['DEVICE_APP_PORT'])))

