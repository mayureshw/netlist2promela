byte states[N_STATES]   // 0,1: given state, 2: uninitialized
bool blockers[N_STATES] // 0: not blocked, 1: blocked

proctype gate(int id) {
    skip
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

inline initInsts() {
    int i = 0;
    do
    :: i < N_INSTS ->
        run gate(i)
    :: else -> break
    od
}

init {
    initStates()
    initInsts()
}
