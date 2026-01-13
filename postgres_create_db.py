
import psycopg
from config import postgres_user, postgres_password, postgres_host, postgres_port, postgres_db


def create_database():
    try:
        # Conectar a PostgreSQL (a la base de datos por defecto 'postgres')
        connection = psycopg.connect(
            f"user={postgres_user} password={postgres_password} host={postgres_host} port={postgres_port} dbname=postgres",
            autocommit=True
        )
        cursor = connection.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{postgres_db}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Crear la base de datos
            cursor.execute(f'CREATE DATABASE {postgres_db}')
            print(f"✅ Base de datos '{postgres_db}' creada exitosamente!")
        else:
            print(f"ℹ️  La base de datos '{postgres_db}' ya existe.")
        
        cursor.close()
        connection.close()
        
    except (Exception, psycopg.Error) as error:
        print(f"❌ Error al crear la base de datos: {error}")


if __name__ == "__main__":
    print("🔧 Iniciando creación de base de datos...")
    create_database()
    print("✅ Proceso completado!")
