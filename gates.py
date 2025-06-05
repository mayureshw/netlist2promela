import json

class Gates:
    def __init__(self,gatesjson):
        gatespec = json.load( open(gatesjson) )
