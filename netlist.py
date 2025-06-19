import sys
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
    def hasBlockUnblock(self): return len(self.blocks) > 0 or len(self.unblocks) > 0
    def fullName(self): return '_'.join([self.instname,self.name])
    def __init__(self,name,direction,nl):
        self.instname,self.name = name.split('.')
        inst = nl.getInst(self.instname)
        inst.registerPin(self.name,direction,self)
        self.id = Pin.cnt
        Pin.cnt = Pin.cnt + 1
        self.blocks = []
        self.unblocks = []

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
    def gateFn(self): return '_'.join([self.typ,str(len(self.ipins)),str(len(self.opins))])
    def argstr(self):
        pins = self.sortedIpins() + self.sortedOpins()
        return ', '.join(p.fullName() for p in pins) + ', ' + ', '.join( ('state[' + p.fullName() + ']') for p in pins )
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
    def pinsWithBlockUnblock(self): return [ p for p in Pin.pins.values() if p.hasBlockUnblock() ]
    def havePinWithBlockUnblock(self): return any( p.hasBlockUnblock() for p in Pin.pins.values() )
    def validateAndSetInit(self):
        for n,p in Pin.pins.items():
            if n not in self.init:
                print('No init value for pin',n,file=sys.stderr)
            else:
                p.init = self.init[n]
        for p in self.init:
            if p not in Pin.pins:
                print('Unknown pin in init spec',p,file=sys.stderr)
    def validateAndSetInp(self):
        self.inpvals = {}
        for p,v in self.evseq.items():
            if p not in Pin.pins:
                print('Unknown pin in evseq spec',p,file=sys.stderr)
            else:
                self.inpvals[Pin.pins[p]] = v
    def __init__(self,gatesjson,modelfile,propfile):
        modelspec = json.load( open(modelfile) )
        self.__dict__.update(modelspec)
        propspec = json.load( open(propfile) )
        self.__dict__.update(propspec)
        self._instnames =  self.stdinsts + sorted(self.insts.keys())
        self._insts = { n:Instance(n,self.insts.get(n,None)) for n in self._instnames }
        self._wires = { i : Wire(i,o,self) for i,o in self.wires.items() }
        self.gates = Gates(gatesjson)
        self.validateAndSetInit()
        self.validateAndSetInp()
        self.applycons = []
        for acons in self.applycons :
            if acons not in self.constraints:
                print('Unknown constraint',acons)
            else: self.applycons.append( self.constraints[acons] )
        for a,b,c in self.applycons:
            ap = Pin.pins[a]
            bp = Pin.pins[b]
            cp = Pin.pins[c]
            ap.blocks.append(cp)
            bp.unblocks.append(cp)
