"""
   _____            __                               __
  /  _  \   _______/  |________  ____  ___________ _/  |_
 /  /_\  \ /  ___/\   __\_  __ \/  _ \/  ___/\__  \\   __\
/    |    \\___ \  |  |  |  | \(  <_> )___ \  / __ \|  |
\____|__  /____  > |__|  |__|   \____/____  >(____  /__|
        \/     \/                         \/      \/
_________
\_   ___ \  ___________   ____
/    \  \/ /  _ \_  __ \_/ __ \
\     \___(  <_> )  | \/\  ___/
 \______  /\____/|__|    \___  >
        \/                   \/
"""


APP_NAME = "astrosat"

VERSION = (1, 0, 1)

__title__ = "django-astrosat-core"
__author__ = "Allyn Treshansky"
__version__ = ".".join(map(str, VERSION))

default_app_config = "astrosat.apps.AstrosatConfig"
