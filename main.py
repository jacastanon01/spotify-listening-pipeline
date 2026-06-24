from pathlib import Path
from sqlite3 import Error

from db import create_connection, init_db, insert_stream, insert_track
from pipeline.spotify import process_data

DATA_DIR = Path("./data")


def main() -> None:
    json_files = list(DATA_DIR.glob("*.json"))
    conn = create_connection("listening_history.db")
    init_db(conn)

    for file in json_files:
        records = process_data(file)
        for record in records:
            track, stream = record
            try:
                insert_track(conn, track)
                insert_stream(conn, stream)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting into table: {e}")
    conn.commit()


if __name__ == "__main__":
    main()
