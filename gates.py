import json

class Gates:
    msgtypes = { 'm_setinp', 'm_setop', 'm_initover' }
    def gateid(self,n): self.gateids[n]
    def __init__(self,gatesjson):
        gatespec = json.load( open(gatesjson) )
        gatenames = sorted( gatespec.keys() )
        self.gateids = { n:i  for i,n in enumerate(gatenames) }
        self.msgids = { n:i  for i,n in enumerate(Gates.msgtypes) }
