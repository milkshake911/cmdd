import sqlite3
from clients.FTXClient import FTXClient



def FTXQuery():
    connection = sqlite3.connect("Database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM ftx_input")
    rows = cursor.fetchall()

    LastRowData = rows[-1]
    return LastRowData



# GET PERPS ONLY
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_perps():
    SYMBOLS = FTXClient.get_futures()
    OnlyPerps = []
    for PerpMarkets in SYMBOLS:
    #print(markets["name"])
        if "perp" in PerpMarkets["name"].lower():
            OnlyPerps.append(PerpMarkets["name"])
    return OnlyPerps