
// TODO for safety a hardware lock should be used
.globl p_gpio_out
.globl p_gpio_out.nstackwords
.globl p_gpio_out.maxtimers
.globl p_gpio_out.maxchanends
.globl p_gpio_out.maxthreads
.linkset p_gpio_out.maxthreads, 0
.linkset p_gpio_out.nstackwords, 0
.linkset p_gpio_out.maxtimers, 0
.linkset p_gpio_out.maxchanends, 0

// TODO for safety a hardware lock should be used
p_gpio_out:
ldw   r11, dp[p_gpio]
out   res[r11], r0
retsp 0

.globl p_gpio_peek
.globl p_gpio_peek.nstackwords
.globl p_gpio_peek.maxtimers
.globl p_gpio_peek.maxchanends
.globl p_gpio_peek.maxthreads
.linkset p_gpio_peek.maxthreads, 0
.linkset p_gpio_peek.nstackwords, 0
.linkset p_gpio_peek.maxtimers, 0
.linkset p_gpio_peek.maxchanends, 0

// TODO for safety a hardware lock should be used
p_gpio_peek:
ldw   r11, dp[p_gpio]
peek r0, res[r11]

retsp 0


