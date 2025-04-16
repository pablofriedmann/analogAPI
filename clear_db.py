import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from analogapi.database import clear_database

if __name__ == "__main__":
    clear_database()