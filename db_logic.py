import sqlite3
from config import DATABASE

statuses = [(_,) for _ in ['В процессе', 'Ещё не начато', 'Завершено']]

class DB_Manager:
    def init(self, database):
        self.database = database

    def _get_connection(self):
        return sqlite3.connect(self.database)

    def create_tables(self):
        conn = self._get_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS status (
                    status_id INTEGER PRIMARY KEY,
                    status_name TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    task_name TEXT NOT NULL,
                    description TEXT,
                    time TEXT,
                    status_id INTEGER,
                    FOREIGN KEY(status_id) REFERENCES status(status_id)
                )
            """)

    def executemany(self, sql, data):
        conn = self._get_connection()
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data = tuple()):
        conn = self._get_connection()
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO status (status_name) VALUES (?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_task(self, data):
        sql = """INSERT INTO tasks (user_id, task_name, time, status_id) 
                 VALUES (?, ?, ?, ?)"""
        self.__executemany(sql, [data])

    def get_statuses(self):
        sql = "SELECT status_name FROM status"
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        return res[0][0] if res else None

    def get_tasks(self, user_id):
        sql = "SELECT * FROM tasks WHERE user_id = ?"
        return self.__select_data(sql, (user_id,))

    def get_task_id(self, task_name, user_id):
        sql = 'SELECT task_id FROM tasks WHERE task_name = ? AND user_id = ?'
        res = self.__select_data(sql, (task_name, user_id))
        return res[0][0] if res else None

    def get_task_info(self, user_id, task_name):
        sql = """
        SELECT task_name, description, time, status_name FROM tasks
        JOIN status ON status.status_id = tasks.status_id
        WHERE task_name = ? AND user_id = ?
        """
        return self.__select_data(sql, (task_name, user_id))

    def update_task(self, param, data):
        sql = f"UPDATE tasks SET {param} = ? WHERE task_name = ? AND user_id = ?"
        self.__executemany(sql, [data])

    def delete_task(self, user_id, task_id):
        sql = "DELETE FROM tasks WHERE user_id = ? AND task_id = ?"
        self.__executemany(sql, [(user_id, task_id)])


if __name__ == 'main':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()