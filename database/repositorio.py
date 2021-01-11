# Conexion y consultas a la base de datos
# Modulo para hacer consultas a PostgreSQL
import psycopg2

# Clase auxiliar para acceder a las funcionalidades de PostgreSQL
class Repositorio:
    # Estos atributos son los que guardan el estado de la conexion
    connection = None
    cursor = None
    # Al iniciar un objeto se conecta a la base de datos
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        try:
            # recibe como parametros los datos de conexión
            self.connection = psycopg2.connect(user=self.user,
                                                password=self.password,
                                                host=self.host,
                                                port=self.port,
                                                database=self.database)
            self.cursor = self.connection.cursor()
            # Print PostgreSQL Connection properties
            print(self.connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            self.cursor.execute("SELECT version();")
            record = self.cursor.fetchone()
            print("You are connected to - ", record, "\n")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
    # Metodo para cerrar el socket de conexión y no dejar conexiones abiertas
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
