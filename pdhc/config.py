import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read('/home/chris/pdhc/etc/pdhc/pdhc.ini')
    return config 

CONF = load_config()
