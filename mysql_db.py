import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn


# ------------------------------------------------------------------------------
# MySQL (Backend) table structuer is

# create table files (
#     id int not null auto_increment primary key,
#     filename varchar(255) not null,
#     filedata longblob not null,
#     uploaded_at timestamp not null default current_timestamp );

# -------------------------------------------------------------------------------

# Upload_file
def upload_file(file):
    if file:
        filename = file.filename
        filedata = file.read()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute( "insert into files (filename, filedata) VALUES (%s, %s)",(filename, filedata))
        conn.commit()

        file_id = cursor.lastrowid
        conn.close()

        return {"id": file_id, "filename": filename}

def get_file_from_db(file_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, filedata FROM files WHERE id=%s", (file_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # (filename, filedata) else None