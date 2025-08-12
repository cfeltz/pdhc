import configparser

def load_config():
    config = configparser.ConfigParser()
    if config.read('/etc/pdhc/pdhc.ini'):
        return config 
    if config.read('etc/pdhc/pdhc.ini'):
        print('here')
        return config
    if config.read('../etc/pdhc/pdhc.ini'):
        return config 
    if config.read('../../etc/pdhc/pdhc.ini'):
        return config 
    if config.read('/home/chris/pdhc/etc/pdhc/pdhc.ini'):
        return config 

CONF = load_config()
