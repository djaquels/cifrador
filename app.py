# Bibliotecas usadas por el proyecto
# Flask bilbioteca WEB
from flask import Flask
from flask import Flask, render_template, redirect, url_for
from flask import request
from flask import jsonify
from flask_cors import CORS
# Crypto es usada para las funciones de seguridad
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
import pem
# Para acceso al sistema de archivos
import os
# Biblioteca para la Base de Datos
from database.repositorio import Repositorio

app = Flask(__name__)
# Permite conexión segura desde fuentes confiables
CORS(app)

#Metodo auxiliar para saber si un usuario existe en los registros.
def existe_usuario(user):
    rep = Repositorio("postgres", "postgres", "127.0.0.1", "5432", "cypher")
    query = "SELECT count(*) FROM users where username = %s "
    rep.cursor.execute(query, (user,))
    total = rep.cursor.fetchone()[0]
    print("Existe usuario:".format(total))
    if int(total) == 0:
        return False
    else:
        return True
# Metodo auxiliar para obtener el total de de usuarios registrados.
def get_usuarios():
    rep = Repositorio("postgres", "postgres", "127.0.0.1", "5432", "cypher")
    query = "SELECT count(*) FROM users "
    rep.cursor.execute(query)
    total = rep.cursor.fetchone()[0]
    return total

# Metodo index, pantalla principal
@app.route('/',methods=['POST','GET','OPTIONS'])
def index():
    total = get_usuarios()
    return render_template('index.html',total=total)
# Metodo encargado de desplegar la lista de usuarios y sus llaves publicas.    
@app.route('/users',methods=['GET','OPTIONS'])
def users_list():
    total = get_usuarios()
    try:
        print("reading users table")
        rep = Repositorio("postgres", "postgres", "127.0.0.1", "5432", "cypher")
        query = "SELECT username,public_key  FROM users  "
        rep.cursor.execute(query)
        data = [ x for x in rep.cursor]
        print(data)
        return render_template('users.html',data=data,total=total)
    except  Exception as e:
        print("error papu")
        return  render_template('users.html',data={},total=total)

 # Metodo que se encarga de registrar usuarios de forma segura.       
@app.route('/generated',methods=['POST','GET','OPTIONS'])
def generate_keys():
    total = get_usuarios()
    if request.method == 'POST':
        user = request.form['user']
        passphrase = request.form['passphrase']
        key = RSA.generate(2048) # investigar unidad de bytes
        private_key = key.export_key('PEM')
        public_key = key.publickey().exportKey('PEM')
        seed = str.encode(passphrase)
        rsa_public_key = RSA.importKey(public_key)
        rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
        encrypted_text = rsa_public_key.encrypt(seed)
        f = open("./private_key.rsa", 'wb')
        f.write( key.export_key('PEM'))
        f.close()
        f = open("./public_key.rsa", 'wb')
        f.write( key.publickey().export_key('PEM'))
        f.close()
        a = open("./private_key.rsa", 'r')
        b = open("./public_key.rsa",'r')
        pk = a.read()
        public = b.read()
        a.close()
        b.close()
        rep = Repositorio("postgres", "postgres", "127.0.0.1", "5432", "cypher")
        query = "INSERT INTO users(username,public_key,passphrase) VALUES(%s,%s,%s)"
        rep.cursor.execute(query,(user,public,encrypted_text))
        rep.connection.commit()
        rep.disconnect()
        print(encrypted_text)
        os.remove("./private_key.rsa") 
        os.remove("./public_key.rsa") 
        return render_template('generated.html',private=pk,public=public,passphrase=encrypted_text,total=total)

# Metodo que apartir de un archivo y el nombre usuario valida la identidad del usuario.
@app.route('/validate',methods=['POST','GET','OPTIONS'])
def validate():
    status = False
    mensaje = ""
    total = get_usuarios()
    if request.method == 'POST':
        user = request.form['user']
        if not existe_usuario(user):
            return render_template('validated.html',status=False, mensaje="No existe el usuario",total=total)
        try:
            rep = Repositorio("postgres", "postgres", "127.0.0.1", "5432", "cypher")
            #decifrando
            user = request.form['user']
            private_key = request.files['private_key']
            print("saving file: {}".format(private_key))
            filename = private_key.filename
            private_key.save(os.path.join("./storage/", filename))
            query = "SELECT passphrase FROM users where username = %s "
            rep.cursor.execute(query, (user,))
            passphrase = rep.cursor.fetchone()[0]
            print('your encrypted_text is : {}'.format(passphrase))
            print("importing key")
            pk = open("./storage/{}".format(filename),"rb")
            rsa_private_key = RSA.importKey(pk.read())
            print("key imported")
            pk.close()
            rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
            decrypted_text = rsa_private_key.decrypt(passphrase)
            print('your decrypted_text is : {}'.format(decrypted_text))
            status = True
            mensaje = "Usuario validado con éxito, las llaves coinciden."
        except  Exception as e:
            status = False
            mensaje = "No coinciden las llaves, no se valido el usuario."
        os.remove("./storage/{}".format(filename)) 
        return render_template('validated.html',status=status,mensaje=mensaje,total=total)
    return render_template('validate.html',total=total)

# Inicializa el servidor WEB para la aplicación.    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8057)
