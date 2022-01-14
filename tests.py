from clients.FTXClient import FTXClient
import app

print(app.FTXQueryLastSymbol())
a = FTXClient.get_position(name="SOL-PERP")["size"]
print(a)

with open("test.txt", "w") as f:
    f.write(str(app.FTXQueryLastSymbol()))