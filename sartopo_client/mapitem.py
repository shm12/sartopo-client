from sartopo_client.abstract import BaseObj

class _MapItem(BaseObj):
    KIND = 'MapItem'
    
    def __init__(self, base_url, data, user_id, client) -> None:
        super(_MapItem, self).__init__(base_url, data, user_id, client)
        self.base_url = f'{base_url}/{self.KIND}'
    
    
