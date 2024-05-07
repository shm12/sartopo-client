import requests
from sartopo_client.auth import MyAuth
from sartopo_client.map import Map

SARTOPO_URL = 'https://sartopo.com'
CALTOPO_URL = 'https://caltopo.com'


class SarTopoClient(object):
    """sartopo.com and caltopo.com API unofficial client

    A convenient class for interacting with sartopo  
    """
    V1 = '/api/v1'
    V0 = '/api/v0'

    ACCT_URL = 'acct'
    FOLDER = 'UserFolder'
    MAP = 'CollaborativeMap'

    def __init__(self, user_id, auth_key, auth_id, base_url=SARTOPO_URL) -> None:
        """Initialize SarTopoClient

        In order to interact with sartopo.com you have to create an OAuth1 app key and secret
        Follow the instructions in https://github.com/elliottshane/sme-sartopo-mapsrv?tab=readme-ov-file#code
        to generate the auth_key (OAuth1 key) and the auth_id (OAuth1 secret, names `code` in the response json)S

        Args:
            user_id (str): sartopo.com user id 
            auth_key (str): OAuth1 key base64 encoded
            auth_id (str): OAuth1 secret
            base_url (str, optional): base url for the remote. Defaults to SARTOPO_URL.
        """
        self.user_id = user_id
        self.auth_key = auth_key
        self.auth_id = auth_id
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = MyAuth(auth_key, auth_id, online=(
            base_url in [CALTOPO_URL, SARTOPO_URL]))

        self.update_user_data()

    def update_user_data(self):
        self.user_data = self.get_user_data()

    def get_user_data(self):
        data = {'full': True}
        uri = f'{self.base_url}/sideload/account/{self.user_id}.json'

        res = self.session.get(uri, json=data)
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to get user data. code: {res.status_code}, reason: {res.text}'
        return res.json()['result']

    # convenient getter methods
    def _list(self, kind, cls=None):
        self.update_user_data()
        ret = self.user_data.get('account', {}).get(kind, [])
        if cls:
            return [cls(self.base_url, i, self.user_id, self) for i in ret]
        return ret

    def list_folders(self):
        return self._list('folders')

    def list_credentials(self):
        return self._list('credentials')

    def list_layers(self):
        return self._list('layers')

    def list_short_links(self):
        return self._list('shortLinks')

    def list_icons(self):
        return self._list('icons')

    def list_tracks(self):
        return self._list('tracks')

    def list_pdfs(self):
        return self._list('pdfs')

    def list_maps(self):
        return self._list('tenants', Map)
    
    def _get_item_by_id(self, item_id, l):
        # We can improve the complexity here but since it is
        # a small list most of the time it's not necessary
        for i in l:
            data = i
            if type(i) is not dict:
                data = i.data
            if data['id'] == item_id:
                return i
        
        raise ValueError(f'could not find {item_id}')
                
        
    def get_map(self, map_id):
        return self._get_item_by_id(map_id, self.list_maps())
    
    def get_folder(self, folder_id):
        return self._get_item_by_id(folder_id, self.list_maps())

    def api_action(self, method, url, json=None):
        res = self.session.request(method, url, json=json)
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to {method} {url}. code: {res.status_code}, reason: {res.text}'
        return res.json()['result']
    # Folder manipulations

    def _base_data(self, cls, title, synced=True, folder_id=None):
        data = {
            "properties": {
                "class": cls,
                "title": title,
                'synced': synced,
                "accountId": self.user_id
            }
        }

        if folder_id:
            data['properties']['folderId'] = folder_id

        return data

    def _folder_data(self, title, synced=True, parent_id=None):
        data = self._base_data(self.FOLDER, title, synced, parent_id)
        return data

    def add_folder(self, title, synced=True, parent_id=None):
        """Adds new folder

        Args:
            title (str): title for the new folder
            synced (bool, optional): wether to set the new folder as synced or not. Defaults to True.
            parent (str, optional): parent folder id. Defaults to ''.

        Returns:
            _type_: _description_
        """
        data = self._folder_data(title, synced, parent_id)
        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.FOLDER}'
        return self.api_action('POST', uri, json=data)

    def delete_folder(self, folder_id):
        """Deletes a folder

        Args:
            folder_id (str): folder id to delete

        Returns:
            _type_: _description_
        """

        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.FOLDER}/{folder_id}'
        return self.api_action('DELETE', uri)

    def update_folder(self, folder_id, title, synced=True, parent_id=''):
        """Updates a folder

        Args:
            folder_id (str): folder id to update
            title (str): title for the folder
            synced (bool, optional): wether to set the new folder as synced or not. Defaults to True.
            parent (str, optional): parent folder id. Defaults to ''.

        Returns:
            _type_: _description_
        """
        data = self._folder_data(title, synced, parent_id)
        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.FOLDER}/{folder_id}'
        return self.api_action('POST', uri, json=data)

# map manipulations
    def _map_data(self, title, synced=True,  parent_id='', sharing='URL', mode='cal', description=None):
        data = self._base_data(self.FOLDER, title, synced, parent_id)
        data['properties']['mode'] = mode
        data['properties']['sharing'] = sharing

        if description:
            data['properties']['description'] = description

        # TODO: fill this data
        data['state'] = {
            "features": [],
            "type": "FeatureCollection"
        }
        return data

    def add_map(self, title, synced=True, parent_folder=None, sharing='URL', mode='cal'):
        """Adds new map

        Args:
            title (str): title for the new map
            synced (bool, optional): wether to set the new map as synced or not. Defaults to True.
            parent (str, optional): parent folder id. Defaults to ''.

        Returns:
            _type_: _description_
        """
        data = self._map_data(title, synced, parent_folder, sharing, mode)
        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.MAP}'
        return self.api_action('POST', uri, json=data)

    def delete_map(self, map_id):
        """Deletes a map

        Args:
            map_id (str): map id to delete

        Returns:
            _type_: _description_
        """

        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.MAP}/{map_id}'
        return self.api_action('DELETE', uri)

    def update_map(self, title, synced=True, parent_folder=None, sharing='URL', mode='cal'):
        """Updates a map

        Args:
            map_id (str): map id to update
            title (str): title for the map
            synced (bool, optional): wether to set the new map as synced or not. Defaults to True.
            parent (str, optional): parent folder id. Defaults to ''.

        Returns:
            _type_: _description_
        """
        data = self._map_data(title, synced, parent_folder, sharing, mode)

        uri = f'{self.base_url}{self.V1}/{self.ACCT_URL}/{self.user_id}/{self.MAP}/{map_id}'
        return self.api_action('POST', uri, json=data)
