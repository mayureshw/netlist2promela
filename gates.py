import json

class Gates:
    def gateid(self,n): self.gateids[n]
    def __init__(self,gatesjson):
        gatespec = json.load( open(gatesjson) )
        gatenames = sorted( gatespec.keys() )
        self.gateids = { n:i  for i,n in enumerate(gatenames) }
