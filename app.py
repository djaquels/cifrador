from flask import Flask
from flask import Flask, render_template
from flask import request
from flask import jsonify
from flask_cors import CORS
from Crypto.PublicKey import RSA
app = Flask(__name__)
CORS(app)

@app.route('/',methods=['POST','GET','OPTIONS'])
def index():
    return render_template('index.html')
@app.route('/generate',methods=['POST','OPTIONS'])  
def generate():
    if request.method == 'POST':
        name = request.form['usuario']
        passpharse = request.form['passphrase']
        prin("Generando llave para {} con seed: {}".format(name,passphrase))
    return render_template('generated.html')  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8057)
