import subprocess
import sys
import json
from collections import Counter
from gates import Gates

class BlockUnblocker:
    def __str__(self): return self.condstr() + ' -> ' + self.actionstr()
    def condstr(self): return ':: ( ( id == ' + self.srcpin.fullName() + ' ) && ( val == ' + self.srcdir + ' ) )'
    def actionstr(self): return self.blockername() + '[' + self.tgtpin.fullName() + '] = ' + self.actionval()
    def blockername(self): return 'block_rise' if self.tgtdir == '1' else 'block_fall'
    def __init__(self,srcpin,srcdir,tgtpin,tgtdir):
        self.srcpin = srcpin
        self.srcdir = srcdir
        self.tgtpin = tgtpin
        self.tgtdir = tgtdir

class Blocker(BlockUnblocker):
    def actionval(self): return '1'
    def __init__(self,s,sd,t,td) : super().__init__(s,sd,t,td)

class Unblocker(BlockUnblocker):
    def actionval(self): return '0'
    def __init__(self,s,sd,t,td) : super().__init__(s,sd,t,td)

class Pin:
    cnt = 0
    pins = {}
    @classmethod
    def get(cls,name,direction,nl):
        if name in cls.pins: return cls.pins[name]
        pinst = Pin(name,direction,nl)
        cls.pins[name] = pinst
        return pinst
    def isfork(self): return len(self.drives) > 1
    def fullName(self): return '_'.join([self.instname,self.name])
    def __init__(self,name,direction,nl):
        self.instname,self.name = name.split('.')
        inst = nl.getInst(self.instname)
        inst.registerPin(self.name,direction,self)
        self.id = Pin.cnt
        Pin.cnt = Pin.cnt + 1
        self.drives = []

class Wire:
    def __init__(self,i,o,nl):
        self.i = Pin.get(i,'i',nl)
        self.o = Pin.get(o,'o',nl)
        self.o.drives.append(self.i)

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

class Prop:
    LTLTOOL='ltl2ba' #alternative: spin
    def neverClaim(self): return subprocess.check_output([self.LTLTOOL,'-f',self.ltl()],text=True)
    def ltl(self):
        typ = self.propspec['type']
        handler = getattr(self, 'handle_' + typ)
        if handler == None :
            print('Unhandled property type',typ)
            sys.exit(1)
        return handler()
    def handle_ltl(self): return self.propspec['ltl']
    def handle_alllive(self):
        return ' || '.join(
            '( <> [] ' + p.fullName() + ' ) || ( <> [] !' + p.fullName() + ' )'
            for p in self.nl.pins() )
    def applycons(self): return self.propspec.get('applycons',[])
    def __init__(self,nl,propspec):
        if 'type' not in propspec:
            print('No property type specified in',propspec)
            sys.exit(1)
        self.nl = nl
        self.propspec = propspec

class Netlist:
    stdinsts = [ 'i_env' ]
    def neverClaim(self): return self.prop.neverClaim()
    def nStates(self): return Pin.cnt
    def nInsts(self): return len(self.instNames())
    def instNames(self): return self._instnames
    def gateCounts(self): return Counter( self.insts.values() )
    def getInst(self,name): return self._insts[name]
    def maxInps(self): return max( len(inst.ipins) for inst in self._insts.values() )
    def maxOps(self): return max( len(inst.opins) for inst in self._insts.values() )
    def nonEnvInsts(self): return [ inst for inst in self._insts.values() if inst.name != 'i_env']
    def pins(self): return Pin.pins.values()
    def validateAndSetInit(self):
        for n,p in Pin.pins.items():
            if n not in self.init:
                p.init = 0
                print('init value defaulted to 0 for pin',n,file=sys.stderr)
            else:
                p.init = self.init[n]
        for p in self.init:
            if p not in Pin.pins:
                print('Unknown pin in init spec',p,file=sys.stderr)
    def cons2pindir(self,consp):
        p,_,d = consp.rpartition('.')
        pin = Pin.pins[p]
        dirn = '1' if d == '^' else '0'
        return pin,dirn
    def forks(self): return [ p for p in Pin.pins.values() if p.isfork() ]
    def __init__(self,gatesjson,modelfile,propfile):
        modelspec = json.load( open(modelfile) )
        self.__dict__.update(modelspec)
        propspec = json.load( open(propfile) )
        self.prop = Prop(self,propspec)
        self._instnames =  self.stdinsts + sorted(self.insts.keys())
        self._insts = { n:Instance(n,self.insts.get(n,None)) for n in self._instnames }
        self._wires = { i : Wire(i,o,self) for i,o in self.wires.items() }
        self.gates = Gates(gatesjson)
        self.validateAndSetInit()
        applycons = []
        # Organize blockers/unblockers by the triggering pin and club actions under it. This will be needed when 1 event triggers multiple block/unblocks
        self.blockers = []
        self.unblockers = []
        for acons in self.prop.applycons() :
            if acons not in self.constraints:
                print('Unknown constraint',acons)
            else: applycons.append( self.constraints[acons] )
        for a,b,c in applycons:
            ap,adir = self.cons2pindir(a)
            bp,bdir = self.cons2pindir(b)
            cp,cdir = self.cons2pindir(c)
            blocker = Blocker(ap,adir,cp,cdir)
            unblocker = Unblocker(bp,bdir,cp,cdir)
            self.blockers.append(blocker)
            self.unblockers.append(unblocker)
