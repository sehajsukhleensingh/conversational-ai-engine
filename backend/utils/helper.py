import uuid
# library to generate a new random thread ID 

class Utitlity:

    def generate_thread_id() -> str:
        """
        this func generates 
        a random thread id using uuid4 function 
        
        """
        thread_id = uuid.uuid4()
        return str(thread_id)