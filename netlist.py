import json
from collections import Counter
from gates import Gates

class Pin:
    cnt = 0
    pins = {}
    @classmethod
    def get(cls,name,direction,nl):
        if name in cls.pins: return cls.pins[name]
        pinst = Pin(name,direction,nl)
        cls.pins[name] = pinst
        return pinst
    def fullName(self): return '_'.join([self.instname,self.name])
    def __init__(self,name,direction,nl):
        self.instname,self.name = name.split('.')
        inst = nl.getInst(self.instname)
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
    def sortedIpins(self): return sorted(self.ipins.values(),key=lambda p:p.name)
    def sortedOpins(self): return sorted(self.opins.values(),key=lambda p:p.name)
    def __init__(self,name,typ):
        self.name = name
        self.id = Instance.cnt
        Instance.cnt = Instance.cnt + 1
        gateinstlist = Instance.gateinsts.get(typ,[])
        self.gateinstid = len(gateinstlist)
        gateinstlist.append(self)
        self.typ = 'g_env' if name == 'i_env' else typ
        if self.typ == None :
            print('Could not set inst typ',name,typ)
            sys.exit(1)
        self.ipins = {}
        self.opins = {}

class Netlist:
    stdinsts = [ 'i_env' ]
    def nStates(self): return Pin.cnt
    def nInsts(self): return len(self.instNames())
    def instNames(self): return self._instnames
    def gateCounts(self): return Counter( self.insts.values() )
    def getInst(self,name): return self._insts[name]
    def maxInps(self): return max( len(inst.ipins) for inst in self._insts.values() )
    def maxOps(self): return max( len(inst.opins) for inst in self._insts.values() )
    def nonEnvInsts(self): return [ inst for inst in self._insts.values() if inst.name != 'i_env']
    def pins(self): return Pin.pins.values()
    def __init__(self,nljson,gatesjson):
        nlspec = json.load( open(nljson) )
        self.__dict__.update(nlspec)
        self._instnames =  self.stdinsts + sorted(self.insts.keys())
        self._insts = { n:Instance(n,self.insts.get(n,None)) for n in self._instnames }
        self._wires = { i : Wire(i,o,self) for i,o in self.wires.items() }
        self.gates = Gates(gatesjson)
