from app import create_app
from requests import get
from flaskwebgui import FlaskUI


def ping(url='http://127.0.0.1:5000/ping'):
	try:
		get('http://127.0.0.1:5000/ping', timeout=1)
		return True
	except:
		pass
	return False


try:

	app = create_app()
	web_gui = FlaskUI(app)

	if ping():
		print('existing')
		web_gui.open_browser()
	else:
		print('new')
		web_gui.run()
except Exception as e:
	print(e)
	pass
	input()