byte state[N_STATES]   // 0,1: given state, 2: uninitialized
bool blocker[N_STATES] // 0: not blocked, 1: blocked
chan c_initInst[N_INSTS] = [0] of { byte, byte }

inline initGate() {
    do
    :: c_initInst[id] ? msg,dat ->
        if
        :: msg == m_gatetype -> gatetyp = dat
        :: msg == m_setop ->
            inpIds[inpcnt] = dat
            inpcnt++
        :: msg == m_setinp ->
            opIds[opcnt] = dat
            opcnt++
        :: msg == m_initover -> break
        :: else -> printf("Unknown message type",msg)
        fi
    od

    // initialize last state to 2
    i=0
    do
    :: i < inpcnt -> last[i] = 2
    :: else -> break
    od

}

// inpcnt restrictions may be relaxed in future
inline validateGate()
{
    if
    :: gatetyp == g_env -> skip
    :: gatetyp == g_latch ->
        assert( inpcnt == 3 )
        assert( opcnt == 1 )
    :: gatetyp == g_mullerc ->
        assert( inpcnt == 2 )
        assert( opcnt == 1 )
    :: gatetyp == g_not ->
        assert( inpcnt == 1 )
        assert( opcnt == 1 )
    :: gatetyp == g_xor ->
        assert( inpcnt == 2 )
        assert( opcnt == 1 )
    :: else -> printf("Uknown gate type",gatetyp)
    fi
}

proctype gate( byte id ) {
    byte inpIds[MAX_INPS]
    byte last[MAX_INPS]
    byte opIds[MAX_OPS]
    byte inpcnt = 0
    byte opcnt = 0
    byte gatetyp
    byte msg, dat
    byte i
    initGate()
    validateGate()
    //do
    //    waitTillInpChange()
    //od
}

proctype wire( byte from, to ) {
    byte last = 2;
    do
    :: state[from] != last ->
        atomic {
            last = state[from]
            state[to] = state[from]
        }
    :: else -> skip
    od
}

inline initStates() {
    byte i = 0;
    do
    :: i < N_STATES ->
        state[i] = 0
        blocker[i] = 0
        i++
    :: else -> break
    od
}

inline createInsts() {
    byte i = 0;
    do
    :: i < N_INSTS ->
        run gate(i)
        i++
    :: else -> break
    od
}

init {
    initStates()
    createInsts()
    initWires() // generated
    initInsts() // generated
}
