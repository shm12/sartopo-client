
class BaseObj(object):
    KIND = 'Abstract'

    def __init__(self, base_url, data, user_id, client) -> None:
        self.host = base_url
        self.data = data
        self.user_id = user_id
        self.client = client
        self.base_url = base_url

    def _url(self):
        url = f'{self.base_url}/{self.KIND}'

        id_ = self.data.get('id', None)
        if id_:  # --> already exists
            url = f'{url}/{id_}'

        return url

    def _create(self, kind, data):
        res = self.client.session.post(self._url(), json=data)
        assert res.sta

    def upload(self):
        """Create or update the object in the remote server
        """
        res = self.client.session.post(self._url(), json=self.data)
        assert res.status_code == 200 and res.json()['status'] == 'ok', f'Failed to upload {self.KIND} data. code: {res.status_code}, reason: {res.text}'
        self.data = res.json()['result']

    def delete(self):
        """Delete the object in the remote server
        """
        res = self.client.session.delete(self._url())
        assert res.status_code == 200, f'Failed to delete {self.KIND} data. code: {res.status_code}, reason: {res.text}'
