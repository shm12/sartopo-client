from sartopo_client.consts import FOLDER, PROPERTIES, FOLDER_ID, ID

class BaseObj(object):
    KIND = 'Abstract'

    def __init__(self, base_url, data, user_id, client, map_=None) -> None:
        self.host = base_url
        self._data = {}
        self.data = data
        self.user_id = user_id
        self.client = client
        self.base_url = base_url
        self.map = map_
    
    @property
    def title(self):
        return self.data[PROPERTIES]['title']
    
    def _set_folder(self, folder):
        if folder.data[PROPERTIES]['class'] != FOLDER:
            raise ValueError(f"can only set folder as folder (got {folder.data[PROPERTIES]['class']})")
        self.data[PROPERTIES][FOLDER_ID] = folder.data[PROPERTIES][ID]
    
    def _set_folder_by_id(self, folder_id):
        self.data[PROPERTIES][FOLDER_ID] = folder_id
    
    def _set_connection(self, base_url, user_id, client):
        self.host = base_url
        self.user_id = user_id
        self.client = client
        self.base_url = base_url

    def fetch(self):
        res = self.client.session.get(self._url())
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to fetch {self.KIND} data. code: {res.status_code}, reason: {res.text}'
        self.data = res.json()['result']

    def _url(self):
        url = f'{self.base_url}/{self.KIND}'

        id_ = self.data.get(ID, None)
        if id_:  # --> already exists
            url = f'{url}/{id_}'

        return url

    def upload(self):
        """Create or update the object in the remote server
        """
        res = self.client.session.post(self._url(), json=self.data)
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to upload {self.KIND} data. code: {res.status_code}, reason: {res.text}'
        self.data = res.json()['result']

    def delete(self):
        """Delete the object in the remote server
        """
        res = self.client.session.delete(self._url())
        assert res.status_code == 200, f'Failed to delete {self.KIND} data. code: {res.status_code}, reason: {res.text}'
