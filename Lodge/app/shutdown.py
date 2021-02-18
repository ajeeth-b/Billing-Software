from flask import Blueprint, request, jsonify
import json, os, signal

shutdown =  Blueprint('shutdown', __name__)

@shutdown.route('/shutdown', methods=['GET'])
def stopServer():
	print('Shutting down app...')
	os.kill(os.getpid(), signal.SIGINT)
	return jsonify({ "success": True, "message": "Server is shutting down..." })
