from mysql.connector import pooling

dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "sistema_papeleria"
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)