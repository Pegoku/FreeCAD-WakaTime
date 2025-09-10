
import freecad.Wakatime as module
from importlib import resources

logo : str

way = resources.files(module) / 'Resources/Icons/Logo.svg'


with resources.as_file(way) as path:
    logo = str( path )