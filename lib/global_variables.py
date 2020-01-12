"""
Created by Joscha Vack on 1/6/2020.
"""

from os.path import join, dirname

# ---------------------------
#   Global config variables
# ---------------------------
root_dir = join(dirname(dirname(__file__)))
resource_dir = join(root_dir, "resources")
settings_path = join(resource_dir, 'settings.json')
settings_extra_path = join(resource_dir, 'settings_extra.json')
whitelist_path = join(resource_dir, 'whitelist.json')
jackpot_path = join(resource_dir, 'jackpot.json')
log_file_path = join(resource_dir, 'log.log')
readme_path = join(root_dir, 'README')

# ---------------------------
#   Parent bot available after Init() is called
# ---------------------------
parent = None
