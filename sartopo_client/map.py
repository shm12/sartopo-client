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

    def get_id(self):
        return self.data.get(PROPERTIES, {}).get(MAP_ID, None) or super(Map, self).get_id()
    
    def public_url(self):
        id_ = self.get_id()
        if not id_:
            return ''
        return urlparse(self._url())._replace(path=f'/m/{id_}').geturl()

    def delete(self):
        return self.client.delete_map(self.get_id())

    def list_items(self):
        res = self.client.session.get(f'{self._url()}/since/0')
        assert res.status_code == 200 and res.json(
        )['status'] == 'ok', f'Failed to fetch map items. code: {res.status_code}, reason: {res.text}'

        self.items_data = res.json()['result']
        self.items = self.parse_items_data()
        return self.items

    def parse_items_data(self):
        items = []

        for i in self.items_data['state']['features']:
            kind = i[PROPERTIES]['class']
            if kind in kind_to_map_item:
                items.append(kind_to_map_item[kind](
                    self._url(), i, self.user_id, self.client))
            else:
                items.append(i)

        return items

    def add_item(self, item: BaseObj):
        """lets you add to the map any map item

        Args:
            item (BaseItem): the item to add to the map

        Returns:
            BaseItem: the item that has been added to the map
        """
        item._set_connection(self._url(), self.user_id, self.client)
        item.map = self
        item.upload()
        return item

    def _add_element(self, data, cls, folder=None):
        if folder:
            if type(folder) is str:
                data[PROPERTIES][FOLDER_ID] = folder
            elif type(folder) is Folder:
                data[PROPERTIES][FOLDER_ID] = folder.get_id()
            else:
                raise ValueError(
                    f'folder must be of type Folder or str as a folder id (got {type(folder)})')
        m = cls(self._url(), data, self.user_id, self.client, map_=self)
        return self.add_item(m)

    def add_marker(self,
                   title,
                   coordinates,
                   description=None,
                   size=1,
                   symbol='point',
                   color="FF0000",
                   rotation=None,
                   folder=None,
                   ) -> Marker:
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

        return self._add_element(data, Marker, folder)

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
                  folder=None,
                  ) -> Shape:

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

        return self._add_element(data, Shape, folder)

    def add_line(self,
                 title,
                 coordinates,
                 description=None,
                 width=2,
                 opacity=1,
                 stroke="#FF0000",
                 pattern="solid",
                 fill="#FF0000",
                 folder=None,
                 ) -> Shape:
        return self.add_shape('LineString',
                              title,
                              coordinates,
                              description,
                              width,
                              opacity,
                              stroke,
                              pattern,
                              fill,
                              folder
                              )

    def add_polygon(self,
                    title,
                    coordinates,
                    description=None,
                    width=2,
                    opacity=1,
                    stroke="#FF0000",
                    pattern="solid",
                    fill="#FF0000",
                    folder=None,
                    ) -> Shape:
        return self.add_shape('Polygon',
                              title,
                              coordinates,
                              description,
                              width,
                              opacity,
                              stroke,
                              pattern,
                              fill,
                              folder,
                              )

    def add_folder(self, title, visible=True, label_visible=True, folder=None) -> Folder:
        data = {
            "properties": {
                "title": title,
                "visible": visible,
                "labelVisible": label_visible
            },
        }

        return self._add_element(data, Folder, folder)

    def add_fleet_live_track(self,
                             title,
                             group,
                             deviceId,
                             stroke_width=2,
                             opacity=1,
                             stroke="#FF0000",
                             pattern="M0 -3 L0 3,,12,F",
                             folder=None
                             ) -> LiveTrack:
        data = {
            "properties": {
                "stroke-opacity": opacity,
                "pattern": pattern,
                "stroke-width": stroke_width,
                "title": title,
                "deviceId": f'FLEET:{group}-{deviceId}',
                "stroke": stroke,
                "class": "LiveTrack",
            }
        }

        return self._add_element(data, LiveTrack, folder)
