import json
import logging.config
import logging
import os
from path import logs_path

os.makedirs("logs", exist_ok=True)

current_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(current_dir, "config.json")

with open(config_path, 'r') as file:
    config = json.load(file)
logging.config.dictConfig(config)

try:
    if os.path.exists(logs_path):
        pass
    else:
        os.mkdir(logs_path)
    path_logs = os.path.join(logs_path, 'log.log')
    open(path_logs, 'a').close()
except Exception as _ex:
    logging.critical(f'Error opening json: {_ex}')


bot_logger = logging.getLogger('BOT')
database_logger = logging.getLogger('DATABASE')
app_logger = logging.getLogger(__name__)
server_logger = logging.getLogger('SERVER')
vk_logger = logging.getLogger('VK_CLIENT')
market_logger = logging.getLogger('MARKET_HANDLER')