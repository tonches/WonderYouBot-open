from enum import Enum

#here is no token, for secure reasons
token = ''
db_file = "/code/userdata/database.vdb"
report  = "/code/userdata/reads_data"
out_path = "/code/reports/"

#i dont care
db_name = 'database'
db_user = 'username'
db_pass = 'secret'
#db_host = '172.17.0.1'
db_host = 'db'
db_port = '5432'


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_ENTER_EGO = "2"
    S_SEND_EMO = "3"
    S_CHANGE_NAME = "4"
