proctype g_latch_2_1( byte d, g, q )
{
    bool last_d = state[d]
    bool last_g = state[g]
    assert( last_g == 0 || last_d == state[q] )
    do
    :: state[d] != last_d || state[g] != last_g ->
        if
        :: state[g] -> state[q] = state[d]
        :: else -> skip
        fi
        last_d = state[d]
        last_g = state[g]
    :: else -> skip
    od
}

proctype g_not_1_1( byte i, o )
{
    bool last_i = state[i]
    assert( last_i != state[o] )
    do
    :: state[i] != last_i ->
        state[o] = last_i
        last_i = state[i]
    :: else -> skip
    od
}

proctype g_mullerc_2_1( byte i0, i1, o )
{
    bool last_i0 = state[i0]
    bool last_i1 = state[i1]
    assert( last_i0 && last_i1 || !state[o] )
    do
    :: state[i0] != last_i0 || state[i1] != last_i1 ->
        if
        :: state[i0] == state[i1] -> state[o] = state[i0]
        :: else -> skip
        fi
        last_i0 = state[i0]
        last_i1 = state[i1]
    :: else -> skip
    od
}

proctype g_xor_2_1( byte i0, i1, o )
{
    bool last_i0 = state[i0]
    bool last_i1 = state[i1]
    assert( state[o] == last_i0 ^ last_i1 )
    do
    :: state[i0] != last_i0 || state[i1] != last_i1 ->
        state[o] = state[i0] ^ state[i1]
        last_i0 = state[i0]
        last_i1 = state[i1]
    :: else -> skip
    od
}

proctype wire( byte to, from )
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
    run verify() // user supplied
    setInp() // user supplied
}
