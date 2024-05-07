from sartopo_client.mapitem import _MapItem
from sartopo_client.abstract import BaseObj
from sartopo_client.consts import *


class Marker(BaseObj):
    KIND = MARKER


class Shape(BaseObj):
    KIND = SHAPE

class LiveTrack(BaseObj):
    KIND = LIVE_TRACK

class Folder(BaseObj):
    KIND = FOLDER
    
    def add_item(self, item):
        try:
            item.data['properties']['folderId'] = self.data['id']
        except:
            raise ValueError(f'cannot add {item} to folder')
        
        return item.upload()


kind_to_map_item = {
    MARKER: Marker,
    SHAPE: Shape,
    FOLDER: Folder
}
