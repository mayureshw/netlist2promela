inline setState( id, val ) {
    if
    :: state[id] != val -> state[id] = val
    :: else -> skip
    fi
}

// NOTE: We do not follow else -> skip pattern in the gate and wire processes
// as it leads to a false livelock detection by spin, leading to early
// inference of acceptance cycles.

proctype g_latch_2_1( byte d, g, q; bool d_init, g_init, q_init )
{
    assert( ( g_init == 0 ) || ( d_init == q_init ) )
    bool last_d = d_init
    bool last_g = g_init
    do
    :: ( ( ( state[d] != last_d ) || ( state[g] != last_g ) ) && state[g] ) ->
        atomic {
            setState(q,state[d])
            last_d = state[d]
            last_g = state[g]
        }
    od
}

proctype g_latchrn_3_1( byte d, g, rn, q; bool d_init, g_init, rn_init, q_init )
{
    assert( !rn_init && !q_init || rn_init && (  !g_init || ( d_init == q_init ) ) )
    bool last_d  = d_init
    bool last_g  = g_init
    bool last_rn = rn_init
    do
    :: ( ( state[d] != last_d ) || ( state[g] != last_g ) || ( state[rn] != last_rn ) ) ->
        if
        :: !state[rn] ->
                atomic {
                    setState(q,0)
                    last_d = state[d]
                    last_g = state[g]
                    last_rn = state[rn]
                }
        :: state[rn] && state[g] ->
                atomic {
                    setState(q,state[d])
                    last_d = state[d]
                    last_g = state[g]
                    last_rn = state[rn]
                }
        :: else -> skip
        fi
    od
}

proctype g_not_1_1( byte i, o; bool i_init, o_init )
{
    assert( i_init != o_init )
    bool last_i = i_init
    do
    :: state[i] != last_i ->
        atomic {
            setState(o,last_i)
            last_i = state[i]
        }
    od
}

proctype g_mullerc_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( i0_init && i1_init || !o_init )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ) && ( state[i0] == state[i1] ) ->
        atomic {
            setState(o,state[i0])
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype g_xor_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == ( i0_init ^ i1_init ) )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ->
        atomic {
            setState(o,state[i0] ^ state[i1])
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype g_xnor_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == !( i0_init ^ i1_init ) )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ->
        atomic {
            setState(o, !( state[i0] ^ state[i1] ))
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype g_or_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == ( i0_init || i1_init ) )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ->
        atomic {
            setState(o,state[i0] || state[i1])
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype g_nor_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == !( i0_init || i1_init ) )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ->
        atomic {
            setState(o,!(state[i0] || state[i1]))
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype g_and_2_1( byte i0, i1, o; bool i0_init, i1_init, o_init )
{
    assert( o_init == ( i0_init && i1_init ) )
    bool last_i0 = i0_init
    bool last_i1 = i1_init
    do
    :: ( state[i0] != last_i0 ) || ( state[i1] != last_i1 ) ->
        atomic {
            setState(o,state[i0] && state[i1])
            last_i0 = state[i0]
            last_i1 = state[i1]
        }
    od
}

proctype wire( byte to, from; bool to_init, from_init )
{
    assert( to_init == from_init )
    bool last_from = from_init
    do
    :: ( state[from] != last_from ) ->
        wait(to,state[from])
        atomic {
            last_from = state[from]
            setState(to,state[from])
        }
    od
}

init
{
    atomic { // calls to generated code
        initStates()
        initWires()
        createInsts()
        postinit()
    }
}
