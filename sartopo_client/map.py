from sartopo_client.abstract import BaseObj
from sartopo_client.map_items import *
from sartopo_client.consts import *
from urllib.parse import urlparse


class Map(BaseObj):
    KIND = MAP

    def __init__(self, base_url, data, user_id, client) -> None:
        super(Map, self).__init__(base_url, data, user_id, client)
        self.base_url = f'{base_url}{client.V1}'
        self.items = []
        self.items_data = {}

    def public_url(self):
        id_ = self.data.get('id', None)
        if not id_:
            return ''
        return urlparse(self._url())._replace(path=f'/m/{id_}').geturl()

    def fetch_items(self):
        res = self.client.session.get(f'{self._url()}/since/0')
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to fetch map items. code: {res.status_code}, reason: {res.text}'

        self.items_data = res.json()['result']
        self.items = self.parse_items_data()
        return self.items

    def parse_items_data(self):
        items = []

        for i in self.items_data['state']['features']:
            kind = i['properties']['class']
            if kind in kind_to_map_item:
                items.append(kind_to_map_item[kind](
                    self._url(), i, self.user_id, self.client))
            else:
                items.append(i)

        return items

    def _add_element(self, data, cls):
        m = cls(self._url(), data, self.user_id, self.client)
        m.upload()
        return m

    def add_marker(self, title, coordinates, description=None, size=1, symbol='point', color="FF0000", rotation=None):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates
            },
            "properties": {
                "title": title,
                "description": description,
                "marker-size": str(size),
                "marker-symbol": symbol,
                "marker-color": color,
                "marker-rotation": rotation
            }
        }

        return self._add_element(data, Marker)

    def add_shape(self,
                  shape_type,
                  title,
                  coordinates,
                  description=None,
                  width=2,
                  opacity=1,
                  stroke="#FF0000",
                  pattern="solid",
                  fill="#FF0000",
                  ):

        data = {
            "properties": {
                "title": title,
                "description": description,
                "stroke-width": width,
                "stroke-opacity": opacity,
                "stroke": stroke,
                "pattern": pattern,
                "fill": fill
            },
            "geometry": {
                "type": shape_type,
                "coordinates": coordinates
            }
        }

        return self._add_element(data, Shape)

    def add_line(self,
                 title,
                 coordinates,
                 description=None,
                 width=2,
                 opacity=1,
                 stroke="#FF0000",
                 pattern="solid",
                 fill="#FF0000",
                 ):
        return self.add_shape('LineString',
                              title,
                              coordinates,
                              description,
                              width,
                              opacity,
                              stroke,
                              pattern,
                              fill)

    def add_polygon(self,
                    title,
                    coordinates,
                    description=None,
                    width=2,
                    opacity=1,
                    stroke="#FF0000",
                    pattern="solid",
                    fill="#FF0000",
                    ):
        return self.add_shape('Polygon',
                              title,
                              coordinates,
                              description,
                              width,
                              opacity,
                              stroke,
                              pattern,
                              fill)

    def add_folder(self, title, visible=True, label_visible=True):
        data = {
            "properties": {
                "title": title,
                "visible": visible,
                "labelVisible": label_visible
            },
        }

        return self._add_element(data, Folder)
