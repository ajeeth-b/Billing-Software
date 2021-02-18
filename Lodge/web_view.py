from app import create_app
import webview

app = create_app()
webview.create_window('Lodge', app)
webview.start()