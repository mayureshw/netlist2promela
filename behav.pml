byte states[N_STATES]   // 0,1: given state, 2: uninitialized
bool blockers[N_STATES] // 0: not blocked, 1: blocked
chan c_initInst[N_INSTS] = [0] of { int, int }

proctype gate( int id ) {
    int inpIds[MAX_INPS]
    int opIds[MAX_OPS]
}

proctype wire( int from, to ) {
    skip;
}

inline initStates() {
    int i = 0;
    do
    :: i < N_STATES ->
        states[i] = 2
        blockers[i] = 0
        i++
    :: else -> break
    od
}

inline createInsts() {
    int i = 0;
    do
    :: i < N_INSTS ->
        run gate(i)
    :: else -> break
    od
}

init {
    initStates()
    createInsts()
    initWires()
    initInsts()
}
