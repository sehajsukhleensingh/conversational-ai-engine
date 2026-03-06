import uuid # library to generate a new random thread ID 
import sqlite3 # lib to connect to sqlite database 

class Utitlity:

    def generate_thread_id() -> str:
        """
        this func generates 
        a random thread id using uuid4 function 
        
        """
        thread_id = uuid.uuid4()
        return str(thread_id)
    

    def extract_threads():
        
        try:
            conn = sqlite3.connect("backend/data/convos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT thread_id from checkpoints")
            data = cursor.fetchall()
            
            threads = [thread[0] for thread in data]

            conn.close()
            return threads
        
        except Exception:
            return []