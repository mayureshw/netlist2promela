byte state[N_STATES];
bool blocker[N_STATES];
bool driver[N_STATES];


init {
    int i = 0;
    do
    :: i < N_STATES -> 
        state[i] = 2; // 2 means undefined
        blocker[i] = 0;
        i++
    :: else -> break
    od
}
