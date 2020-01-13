"""
Created by Joscha Vack on 1/6/2020.
"""

from os.path import join, dirname

# ---------------------------
#   Global config variables
# ---------------------------
root_dir = join(dirname(dirname(__file__)))
resource_dir = join(root_dir, "resources")
config_file = join(resource_dir, 'settings.json')
whitelist_file = join(resource_dir, 'whitelist.json')
jackpot_file = join(resource_dir, 'jackpot.json')
log_dir = join(resource_dir, 'log')
log_file = None
readme_file = join(root_dir, 'README')

# ---------------------------
#   Parent bot available after Init() is called
# ---------------------------
parent = None
