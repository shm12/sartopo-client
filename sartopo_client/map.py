from sartopo_client.abstract import BaseObj
from sartopo_client.map_items import *
from sartopo_client.consts import *


class Map(BaseObj):
    KIND = MAP

    def __init__(self, base_url, data, user_id, client) -> None:
        super(Map, self).__init__(base_url, data, user_id, client)
        self.base_url = f'{base_url}{client.V1}/map/{data["id"]}'

    def _add_element(self, data, cls):
        m = cls(self.base_url, data, self.user_id, self.client)
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
