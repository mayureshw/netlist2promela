bool state[N_STATES]
bool blocker[N_STATES]

proctype g_latch_2_1( bool d, g, q )
{
    assert( g == 0 || d == q )
}

proctype g_mullerc_2_1( bool i0, i1, o )
{
    assert( i0 && i1 || ! o )
}

proctype g_not_1_1( bool i, o )
{
    assert( i != o )
}

proctype g_xor_2_1( bool i0, i1, o )
{
    assert( o == i0 ^ i1 )
}

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
