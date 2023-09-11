# with love, from JMo <3
# 2023-09-11 00:20:49.948557 from programs/mal/fives.mal
#
    LOAD r13,const_100
   STORE  r13,var_x
while_do_1:
    LOAD r14,var_x
    LOAD r12,const_0
   SUB  r0,r14,r12
   JUMP/ZM  od_2  #>
    LOAD r11,var_x
    LOAD r10,const_5
    LOAD r9,var_x
    LOAD r8,const_5
   DIV  r9,r9,r8
   MUL  r10,r10,r9
   SUB  r11,r11,r10
   STORE  r11,var_remainder
    LOAD r12,var_remainder
    LOAD r10,const_0
   SUB  r0,r12,r10
   JUMP/PM  else_3  #==
    LOAD r12,var_x
   STORE  r12,r0,r0[511]
    JUMP  fi_4
else_3:
fi_4:
    LOAD r14,var_x
    LOAD r11,const_1
   SUB  r14,r14,r11
   STORE  r14,var_x
   JUMP  while_do_1
od_2:
	HALT  r0,r0,r0
const_0:  DATA 0
const_1:  DATA 1
const_5:  DATA 5
const_100:  DATA 100
var_remainder: DATA 0
var_x: DATA 0
