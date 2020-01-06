"""
Created by Joscha Vack on 1/5/2020.
"""

from os.path import join, dirname

# ---------------------------
#   Script Information [Required]
# ---------------------------
script_name = "JBetSystem"
website = "https://www.streamlabs.com"
description = "blah"
creator = "KanjiuAkuma"
version = "1.0.0.0"


# ---------------------------
#   Global config variables
# ---------------------------
resource_dir = join(dirname(dirname(__file__)), "resources")
settings_path = join(resource_dir, 'settings.json')

parent = None
