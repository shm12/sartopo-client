from sartopo_client.mapitem import _MapItem
from sartopo_client.abstract import BaseObj
from sartopo_client.consts import *
from sartopo_client.utils import assert_res
import requests


class Marker(BaseObj):
    KIND = MARKER


class Shape(BaseObj):
    KIND = SHAPE


class LiveTrack(BaseObj):
    KIND = LIVE_TRACK
    
    def get_type_group_device(self):
        """Get the type of the LiveTrack, the group and the device id

        Returns:
            tuple: (type, group, device_id)
        """
        splitted = self.data[PROPERTIES]['deviceId'].split('-')
        group = splitted.pop(0).split(':')
        track_type = group.pop(0)
        
        group = ':'.join(group)
        device_id = '-'.join(splitted)
        
        return track_type, group, device_id
        
    def report(self, latitude, longitude):
        """report current location of the device

        Args:
            latitude (int): latitude
            longitude (int): longitude

        Raises:
            NotImplementedError: for none FLEET LiveTracks
        """
        track_type, group, device_id = self.get_type_group_device()
        params = {
            'id': device_id,
            'lat': latitude,
            'lng': longitude
        }
        
        if track_type == 'FLEET':
            assert_res(requests.get(
                f'{self.client.base_url}{self.client.V1}/position/report/{group}', params=params))
            return
        
        # TODO: implement other types
        
        raise NotImplementedError('cannot report other types than FLEET LiveTrack')


class Folder(BaseObj):
    KIND = FOLDER

    def add_item(self, item):
        """Adds an item to the folder (and potentially remove it from it's old one)

        Args:
            item (BaseObj): item to insert to the folder

        Raises:
            ValueError: invalid item has been provided
        """
        try:
            item.data[PROPERTIES][FOLDER_ID] = self.data[ID]
        except:
            raise ValueError(f'cannot add {item} to folder')

        item._set_connection(self.base_url, self.user_id, self.client)

        return item.upload()
    
    def remove_item(self, item: BaseObj):
        """removes the given item from the list

        Args:
            item (BaseObj): item to be removed
        """
        # TODO: validate it's in the folder?
        
        item.data[PROPERTIES][FOLDER_ID] = ''
        item.upload()
    
    def list_items(self):
        """list all the items inside this folder

        Returns:
            list: items inside the folder
        """
        assert self.map, 'cannot list folder that is not inside a map'
        map_items = self.map.list_items()
        return [i for i in map_items if i.data[PROPERTIES][FOLDER_ID] == self.data[PROPERTIES][FOLDER_ID]]


class Locator(BaseObj):
    KIND = LOCATOR


class AppTrack(BaseObj):
    KIND = APP_TRACK


class Assignment(BaseObj):
    KIND = ASSIGNMENT


class Clue(BaseObj):
    KIND = CLUE


class FieldTrack(BaseObj):
    KIND = FIELD_TRACK


class FieldWaypoint(BaseObj):
    KIND = FIELD_WAYPOINT


class MapMediaObject(BaseObj):
    KIND = MAP_MEDIA_OBJECT


kind_to_map_item = {
    MARKER: Marker,
    SHAPE: Shape,
    FOLDER: Folder,
    LIVE_TRACK: LiveTrack,
    LOCATOR: Locator,
    APP_TRACK: AppTrack,
    ASSIGNMENT: Assignment,
    CLUE: Clue,
    FIELD_TRACK: FieldTrack,
    FIELD_WAYPOINT: FieldWaypoint,
    MAP_MEDIA_OBJECT: MapMediaObject,
}
