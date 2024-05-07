from sartopo_client.mapitem import _MapItem
from sartopo_client.abstract import BaseObj
from sartopo_client.consts import *

class Marker(BaseObj):
    KIND = MARKER

class Shape(BaseObj):
    KIND = SHAPE

class Folder(BaseObj):
    KIND = FOLDER