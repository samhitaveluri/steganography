from flask import Flask, request, render_template, send_file, redirect, url_for
from stegano import lsb
import os
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_FOLDER'] = 'secrets'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['SECRET_FOLDER']):
    os.makedirs(app.config['SECRET_FOLDER'])

@app.route('/')
def index():
    return render_template('Stego_web_page.html')

@app.route('/embed', methods=['POST'])
def embed():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    message = request.form['message']
    password = request.form['password'] or "no_password_given"
    
    if file.filename == '':
        return 'No selected file'
    
    if file and file.filename.endswith('.png'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        embed_message = password + " " + message
        secret = lsb.hide(filepath, embed_message)
        random_num = random.randint(0, 100)
        filename = f"secret{random_num}.png"
        secret_filepath = os.path.join(app.config['SECRET_FOLDER'], filename)
        secret.save(secret_filepath)
        
        return send_file(secret_filepath, as_attachment=True)

    return 'Please upload a .png file'

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    password = request.form['password']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and file.filename.endswith('.png'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            message = lsb.reveal(filepath)
            if password in message:
                message = message.replace(password, "")
                return f"The secret message is: {message}"
            else:
                return "Couldn't reveal the message with the passcode."
        except Exception as e:
            return str(e)
    
    return 'Please upload a .png file'

if __name__ == '__main__':
    app.run(debug=True)
