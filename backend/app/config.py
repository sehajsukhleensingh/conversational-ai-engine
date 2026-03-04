from backend.utils.helper import Utitlity


class Config:

    def config_id():

        thread_id = Utitlity.generate_thread_id()
        CONFIG = {"configurable":{"thread_id":thread_id}}

        return CONFIG