# parse arguments and create a database
import argparse
import sqlite3
import os
import sys

PATH = "sb.sqlite3"


def create_db():
    # create a new empty database file and make the
    # tables required for the bot to function
    #
    # table : connections
    # table : nicknames
    print("Creating database")

    try:
        # check if the file exists
        print(f"Checking if {PATH} exists...")
        if os.path.exists(PATH):
            print(f"{PATH} already exists.")
            if input("Do you want to overwrite it? (y/n): ").lower() != "y":
                print("Exiting...")
                sys.exit(0)

            print("Removing existing database...")
            os.remove(PATH)
            print("Database removed.")

        print(f"Connecting to {PATH}...")
        conn = sqlite3.connect(PATH)

        # make a table with the first field being a unique integer key and a second text field for the connection
        print(f"Creating table 'connections' in {PATH}...")
        conn.execute("CREATE TABLE connections (server TEXT PRIMARY KEY, channel TEXT)")
        # make a table with the first field being a unique text key with the username and a second text field for the nickname
        print(f"Creating table 'nicknames' in {PATH}...")
        conn.execute(
            "CREATE TABLE nicknames (username TEXT PRIMARY KEY, nickname TEXT)"
        )

        # populating with basic data
        print("Populating table 'nicknames' with basic data...")

        standard_nicknames = {"skarask": "Ganf", "highwind": "Kain", "frahbrah": "Kef"}

        for username, nickname in standard_nicknames.items():
            conn.execute(
                "INSERT INTO nicknames (username, nickname) VALUES (?, ?)",
                (username, nickname),
            )

        conn.commit()

        print("Closing connection...")
        conn.close()
        print("Connection closed.")
        create_voices()
    except Exception as e:
        print(f"Error during create_db: {e}")
        pass


def create_table(table_name: str, table_creation_query: str) -> None:
    try:
        conn = sqlite3.connect(PATH)
        # attempt to delete the table first
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(table_creation_query)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error during create_table: {e}")
        pass


def create_voices():
    create_table(
        table_name="voices",
        table_creation_query="""
CREATE TABLE voices (username TEXT PRIMARY KEY, voice TEXT)
        """,
    )


def create_voice_download_queue():
    create_table(
        table_name="voice_download_queue",
        table_creation_query="""
CREATE TABLE voice_download_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
  requested_by_username TEXT,
  requested_filename TEXT,
  youtube_url TEXT,
  processed INTEGER DEFAULT 0 CHECK(processed IN (0, 1))
);

                 """,
    )


def main():
    print("SonicBlaster DB Manager")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--create-db", action="store_true", help="create an empty database"
    )
    parser.add_argument(
        "-cv",
        "--create-voices",
        action="store_true",
        help="create voices table",
    )
    parser.add_argument(
        "-cd",
        "--create-download",
        action="store_true",
        help="create voice_download_queue table",
    )
    parser.add_argument("-n", "--nicknames", action="store_true", help="list nicknames")

    args = parser.parse_args()

    # if no arguments are passed, print the help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.create_db:

        create_db()

    if args.create_voices:

        create_voices()

    if args.create_download:

        create_voice_download_queue()

    if args.nicknames:
        print("Nicknames:")

        try:
            conn = sqlite3.connect(PATH)

            cursor = conn.execute("SELECT * FROM nicknames")

            for row in cursor:
                print(row)

            conn.close()

        except Exception as e:
            print(f"Error during main: {e}")
            pass


def load_nicknames() -> dict:
    # load the nicknames from the database
    nicknames = {}

    try:
        conn = sqlite3.connect(PATH)

        cursor = conn.execute("SELECT * FROM nicknames")

        for row in cursor:
            nicknames[row[0]] = row[1]

        conn.close()

    except Exception as e:
        print(f"Error during load_nicknames: {e}")
        pass

    return nicknames


def load_voices() -> dict:
    # load the voices from the database
    voices = {}

    try:
        conn = sqlite3.connect(PATH)

        cursor = conn.execute("SELECT * FROM voices")

        for row in cursor:
            voices[row[0]] = row[1]

        conn.close()

    except Exception as e:
        print(f"Error during load_voices: {e}")
        pass

    return voices


def register_voice(username: str, voice: str) -> None:
    try:
        conn = sqlite3.connect(PATH)

        # attempt to remove the existing username first
        conn.execute("DELETE FROM voices WHERE username = ?", (username,))

        conn.execute(
            "INSERT INTO voices (username, voice) VALUES (?, ?)",
            (username, voice),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error during register_nickname: {e}")
        pass


def register_nickname(username: str, nickname: str) -> None:
    try:
        conn = sqlite3.connect(PATH)

        # attempt to remove the existing username first
        conn.execute("DELETE FROM nicknames WHERE username = ?", (username,))

        conn.execute(
            "INSERT INTO nicknames (username, nickname) VALUES (?, ?)",
            (username, nickname),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error during register_nickname: {e}")
        pass


if __name__ == "__main__":
    main()
