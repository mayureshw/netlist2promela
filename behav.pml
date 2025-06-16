proctype g_latch_2_1( byte d, g, q; bool d_init, g_init, q_init )
{
    assert( g_init == 0 || d_init == q_init )
    bool last_d = d_init
    bool last_g = g_init
    do
    :: state[d] != last_d || state[g] != last_g ->
        atomic {
            if
            :: state[g] -> state[q] = state[d]
            :: else -> skip
            fi
            last_d = state[d]
            last_g = state[g]
        }
    :: else -> skip
    od
}

proctype g_not_1_1( byte i, o; bool i_init, o_init )
{
    assert( i_init != o_init )
    bool last_i = i_init
    do
    :: state[i] != last_i ->
        atomic {
            state[o] = last_i
            last_i = state[i]
        }
    :: else -> skip
    od
}

proctype g_mullerc_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( i0_init && i1_init || !o_init )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: state[i0] != last_i0 || state[i1] != last_i1 ->
        atomic {
            if
            :: state[i0] == state[i1] -> state[o] = state[i0]
            :: else -> skip
            fi
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    :: else -> skip
    od
}

proctype g_xor_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == i0_init ^ i1_init )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: state[i0] != last_i0 || state[i1] != last_i1 ->
        atomic {
            state[o] = state[i0] ^ state[i1]
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    :: else -> skip
    od
}

proctype wire( byte to, from; bool to_init, from_init )
{
    assert( to_init == from_init )
    bool last_from = from_init
    do
    :: state[from] != last_from ->
        atomic {
            last_from = state[from]
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
        setInp() // user supplied
    }
}
