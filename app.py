import random
import string
from flask import Flask
from flaskext.mysql import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
app = Flask(__name__)
mysql = MySQL()
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2 per minute", "1 per second"],
    storage_uri="memory://",
    # Redis
    # storage_uri="redis://localhost:6379",
    # Redis cluster
    # storage_uri="redis+cluster://localhost:7000,localhost:7001,localhost:70002",
    # Memcached
    # storage_uri="memcached://localhost:11211",
    # Memcached Cluster
    # storage_uri="memcached://localhost:11211,localhost:11212,localhost:11213",
    # MongoDB
    # storage_uri="mongodb://localhost:27017",
    # Etcd
    # storage_uri="etcd://localhost:2379",
    strategy="fixed-window", # or "moving-window"
)

app.config.from_object(Config)

mysql.init_app(app)

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/')
@limiter.limit("2 per hour")
def index():
    # Establish a connection to the MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()


    # Generate random username and password
    username = generate_random_string(8)
    password = generate_random_string(12)
    db = generate_random_string(12)

    # Create a new database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}")

    # Create a new user and grant privileges on the new database
    cursor.execute(f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}'")
    cursor.execute(f"GRANT ALL PRIVILEGES ON {db}.* TO '{username}'@'localhost'")

    # Close the database connection
    cursor.close()
    conn.close()

    return f"New database '{db}' created. Username: {username}, Password: {password}"

if __name__ == '__main__':
    app.run()
