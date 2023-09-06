"""
Instruction format for the Duck Machine 2022 (DM2022),
a simulated computer modeled loosely on the ARM processor
found in many cell phones, the Raspberry Pi, and
(with modifications) recent models of Apple Macintosh.

Instruction words are unsigned 32-bit integers
with the following fields (from high-order to low-order bits).  
All are unsigned except offset, which is a signed value in 
range -2^11 to 2^11 - 1. 

See docs/duck_machine.md for details. 
"""

import context #search from proj root
from instruction_set.bitfield import BitField
