bool state[N_STATES]   // 0,1: given state, 2: uninitialized
bool blocker[N_STATES] // 0: not blocked, 1: blocked


proctype wire( byte from, to )
{
    assert( state[from] == state[to] )
    bool last = state[from]
    do
    :: state[from] != last ->
        atomic {
            last = state[from]
            state[to] = state[from]
        }
    :: else -> skip
    od
}

init
{
    atomic {
        initStates() // generated
        initWires() // generated
        createInsts() // generated
    }
    setInp() // user supplied
    verify() // user supplied
}
