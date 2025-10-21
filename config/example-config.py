"""
Main configuration for Spigot Updater
Copy this file to config.py and customize for your setup
"""

config = {
    'server_name': 'Left4Craft',
    'color': '#C10053',
    'channel_id': '731316455924039722',
    'server_jars_api': 'papermc',  # papermc | serverjars
    'left4status': 'https://status.left4craft.org/',  # optional
    'headless_browser': True,
    'no_sandbox_browser': False,  # only change to True if you are getting errors or using docker
    'cloudflare_timeout': 300000,  # time to wait to pass cloudflare Javascript challenge
    'navigation_delay': 10000,  # delay between navigating spigotmc pages
    'download_time': 10000,  # 10-15 seconds recommended, 5 seconds for Cloudflare
    'save_logs': True,
    'debug': False,
}

# For backwards compatibility
DEBUG = config['debug']
SAVE_LOGS = config['save_logs']
