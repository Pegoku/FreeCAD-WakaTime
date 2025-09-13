
import freecad.Wakatime as module
from importlib import resources


icons = resources.files(module) / 'Resources/Icons'


def icon ( name : str ):

    file = name + '.svg'

    icon = icons / file

    with resources.as_file(icon) as path:
        return str( path )