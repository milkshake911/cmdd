from FTX.api import FtxClient
from configs import FTXConfig 

FTXClient = FtxClient(api_key=FTXConfig.api_keyFTX,api_secret=FTXConfig.api_secretFTX)

