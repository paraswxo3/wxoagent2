from flask import Flask
from flask_cors import CORS
from flask import send_file

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

@app.route('/download')
def download_pdf():
    return send_file("171120231905-CorrigendumFormatsWithAmount2.pdf", as_attachment=True)  # Downloads the file

@app.route('/view')
def view_pdf():
    return send_file("New Windows 11 Known Issues Keep Coming.pdf", mimetype='application/pdf')  # Opens in browser

if __name__ == '__main__':
    app.run(debug=True)