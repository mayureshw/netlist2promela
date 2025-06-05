import json
from collections import Counter

class Pin:
    cnt = 0
    pins = {}
    @classmethod
    def get(cls,name,direction,nl):
        if name in cls.pins: return cls.pins[name]
        pinst = Pin(name,direction,nl)
        cls.pins[name] = pinst
        return pinst
    def __init__(self,name,direction,nl):
        instname,self.name = name.split('.')
        inst = nl.getInst(instname)
        inst.registerPin(self.name,direction,self)
        self.id = Pin.cnt
        Pin.cnt = Pin.cnt + 1

class Wire:
    def __init__(self,i,o,nl):
        self.i = Pin.get(i,'i',nl)
        self.o = Pin.get(o,'o',nl)

class Instance:
    cnt = 0
    gateinsts = {}
    def registerPin(self,pinname,direction,pinobj):
        pinstore = self.ipins if direction == 'i' else self.opins
        if pinname in pinstore :
            print('Attempt to register same pin again',self.name,pinname,direction)
            sys.exit(1)
        pinstore[pinname] = pinobj
    def __init__(self,name,typ):
        self.name = name
        self.id = Instance.cnt
        Instance.cnt = Instance.cnt + 1
        gateinstlist = Instance.gateinsts.get(typ,[])
        self.gateinstid = len(gateinstlist)
        gateinstlist.append(self)
        self.typ = 'env' if name == 'env' else typ
        if self.typ == None :
            print('Could not set inst typ',name,typ)
            sys.exit(1)
        self.ipins = {}
        self.opins = {}

class Netlist:
    stdinsts = [ 'env' ]
    def nStates(self): return Pin.cnt
    def instNames(self): return self._instnames
    def gateCounts(self): return Counter( self.insts.values() )
    def getInst(self,name): return self._insts[name]
    def __init__(self,nljson):
        nlspec = json.load( open(nljson) )
        self.__dict__.update(nlspec)
        self._instnames =  self.stdinsts + sorted(self.insts.keys())
        self._insts = { n:Instance(n,self.insts.get(n,None)) for n in self._instnames }
        self._wires = { i : Wire(i,o,self) for i,o in self.wires.items() }
