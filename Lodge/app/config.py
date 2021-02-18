from os import path, mkdir, getcwd 

FOLDER_NAME = 'data_download'
FILE_NAME = 'lodge_data.csv'

folder = path.join(getcwd(), FOLDER_NAME)
if not path.exists(folder):
	mkdir(folder)
file_path = path.join(folder, FILE_NAME)

config = {
	'SECRET_KEY' : 'thesecret',
	'SQLALCHEMY_DATABASE_URI' : 'sqlite:///lodge.db',
	'SQLALCHEMY_TRACK_MODIFICATIONS' : True,
	'ADMIN_USERS' : ['admin@gmail.com'],
	'ADMIN_EMAIL' : 'admin@gmail.com',
	'ADMIN_PASSWORD' : 'admin',
	'DATA_FOLDER':folder,
	'DATA_FILENAME':FILE_NAME,
	'DATA_FILE' : file_path,
}
