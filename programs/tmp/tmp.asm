# with love, from JMo <3
# 2023-09-10 21:11:22.887574 from programs/mal/print.mal
#
    LOAD r12,const_7
   STORE  r12,var_x
    LOAD r13,const_8
   STORE  r13,var_y
    LOAD r14,var_x
    LOAD r12,var_y
   ADD  r14,r14,r12
   STORE  r14,r0,r0[511]
	HALT  r0,r0,r0
const_7:  DATA 7
const_8:  DATA 8
var_x: DATA 0
var_y: DATA 0
