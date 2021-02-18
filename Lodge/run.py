from app import create_app

app = create_app()

DEBUG = False
DEBUG = True

if __name__ == '__main__':
	app.run(debug=DEBUG)