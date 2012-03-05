#include <xs1.h>

.section        .cp.const4,"aMc",@progbits,4
.align  4
P32A_ID:
.long  XS1_PORT_32A
.text

.globl port32A_out
.globl port32A_out.nstackwords
.globl port32A_out.maxtimers
.globl port32A_out.maxchanends
.globl port32A_out.maxthreads
.linkset port32A_out.maxthreads, 0
.linkset port32A_out.nstackwords, 0
.linkset port32A_out.maxtimers, 0
.linkset port32A_out.maxchanends, 0

// TODO for safety a hardware lock should be used
port32A_out:
ldw   r11, cp[P32A_ID]
out   res[r11], r0
retsp 0

.globl port32A_peek
.globl port32A_peek.nstackwords
.globl port32A_peek.maxtimers
.globl port32A_peek.maxchanends
.globl port32A_peek.maxthreads
.linkset port32A_peek.maxthreads, 0
.linkset port32A_peek.nstackwords, 0
.linkset port32A_peek.maxtimers, 0
.linkset port32A_peek.maxchanends, 0


// TODO for safety a hardware lock should be used
port32A_peek:
ldw   r11, cp[P32A_ID]
peek r0, res[r11]

retsp 0
