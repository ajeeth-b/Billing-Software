from app import create_app
from requests import get
from flaskwebgui import FlaskUI

# def ping(url='http://127.0.0.1:5000/ping'):
# 	try:
# 		get('http://127.0.0.1:5000/ping', timeout=1)
# 		return True
# 	except:
# 		pass
# 	return False

def kill_old_app():
	try:
		get('http://127.0.0.1:5000/shutdown', timeout=1)
	except Exception as e:
		pass

try:
	kill_old_app()
	app = create_app()
	web_gui = FlaskUI(app)
	web_gui.run()
except Exception as e:
	print(e)
