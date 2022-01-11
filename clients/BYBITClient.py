from bybit import bybit
from BybitWebsocket import BybitWebsocket
from configs import BYBITConfig


# Client Bybit API 
BBClient = bybit(test=False,api_key=BYBITConfig.api_key,api_secret=BYBITConfig.api_secret)

# Websocket Bybit
ws = BybitWebsocket(wsURL="wss://stream.bybit.com/realtime",api_key=BYBITConfig.api_key,api_secret=BYBITConfig.api_secret)