# Conexion y consultas a la base de datos
import psycopg2


class Repositorio:
    connection = None
    cursor = None

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        try:
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

    def disconnect(self):
        self.cursor.close()
        self.connection.close()
