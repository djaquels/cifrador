from flask import Flask
from flask import Flask, render_template, redirect, url_for
from flask import request
from flask import jsonify
from flask_cors import CORS
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

from database.repositorio import Repositorio

app = Flask(__name__)
CORS(app)

@app.route('/',methods=['POST','GET','OPTIONS'])
def index():
    return render_template('index.html')
@app.route('/generated',methods=['POST','GET','OPTIONS'])
def generate_keys():
    if request.method == 'POST':
        user = request.form['user']
        passphrase = request.form['passphrase']
        key = RSA.generate(2048)
        private_key = key.export_key('PEM')
        public_key = key.publickey().exportKey('PEM')
        seed = str.encode(passphrase)
        rsa_public_key = RSA.importKey(public_key)
        rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
        encrypted_text = rsa_public_key.encrypt(seed)
        rep = Repositorio("postgres", "*sametsiS1", "127.0.0.1", "5432", "cypher")
        query = "INSERT INTO users(username,public_key,passphrase) VALUES(%s,%s,%s)"
        rep.cursor.execute(query,(user,public_key,encrypted_text))
        rep.connection.commit()
        rep.disconnect()
        return render_template('generated.html',private=private_key)
@app.route('/validate',methods=['POST','GET','OPTIONS'])
def validate():
    if request.method == 'POST':
        rep = Repositorio("postgres", "*sametsiS1", "127.0.0.1", "5432", "cypher")
        #decifrando
        user = request.form['user']
        private_key = request.form['private_key']
        query = "SELECT passphrase FROM users where username = %s "
        rep.cursor.execute(query, (user))
        passphrase = rep.cursor.fetchone()
        f = open("D:\MAESTROS\Cifrado\private.txt", "r")
        pk = f.read()
        print('your encrypted_text is : {}'.format(passphrase))
        print(private_key)
        rsa_private_key = RSA.importKey(pk)
        rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
        decrypted_text = rsa_private_key.decrypt(passphrase)
        print('your decrypted_text is : {}'.format(decrypted_text))
        return render_template('validated.html')
    return render_template('validate.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8057)
