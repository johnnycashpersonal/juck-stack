
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
from enum import Enum, Flag

#The field bit positions
reserved = BitField(31,31)
op_field = BitField(26, 30)
cond_field = BitField(22, 25)
reg_target_field = BitField(18, 21)
reg_src1_field = BitField(14, 17)
reg_src2_field = BitField(10, 13)
offset_field = BitField(0, 9)


#The Operation Codes (OpCodes)
class OpCode(Enum):
    """The operation codes specify what the CPU and ALU should do."""
    #CPU control (beyond ALU)

    HALT = 0 # Stop the computer simulation (in Duck Machine Proj)
    LOAD = 1 # Transfer from memory to register
    STORE = 2 # Transfer from registry to memory

    #ALU Operations
    ADD = 3 # Addition
    SUB = 5 # Subtraction
    MUL = 6 # Multiplication
    DIV = 7 # Int Division like // in python

#conditions for operations (ie go if this)
class CondFlag(Flag):
    """The condition mask in an instruction and the format
    of the condition code register are the same, so we can 
    logically and them to predicate an instruction. 
    """
    M =1  # Minus (negative)
    Z =2  # Zero
    P =4  # Positive
    V =8  # Overflow (arithmetic error, e.g., divide by zero)
    NEVER =0
    ALWAYS =M|Z|P|V

    """Flag	 Decimal value	4-bit binary
        M	   1 = 2^0	     0001
        Z	   2 = 2^1	     0010
        P	   4 = 2^2	     0100
        V	   8 = 2^3	     1000
        NEVER	  0	         0000
        ALWAYS	  15	     1111"""

    def __str__(self):
        """If the exact combination has a name, we return that.
        Otherwise, we combine bits, e.g., ZP for non-negative.
        """
        for i in CondFlag.__members__.values():
            # Note: Since Python 3.11, the iterator for a Flag does not return
            # "alias members" like ALWAYS, which is why we need __members__.values()
            # to iterate all named flag values including ALWAYS and NEVER.
            if self.value == i.value:
                return i.name

        # No exact alias; give name as sequence of bit names
        bits = []
        for i in CondFlag:
            # The following test is designed to exclude
            # the special combinations 'NEVER' and 'ALWAYS'
            masked = self & i
            if masked and masked is i:
                bits.append(i.name)
        return "".join(bits)
    
"""Registers are numbered from 0 to 15, and have names
like r3, r15, etc.  Two special registers have additional
names:  r0 is called 'zero' because on the DM2022 it always
holds value 0, and r15 is called 'pc' because it is used to
hold the program counter.
"""

NAMED_REGS = {
    "r0": 0, "zero": 0,
    "r1": 1, "r2": 2, "r3": 3, "r4": 4, "r5": 5, "r6": 6, "r7": 7, "r8": 8,
    "r9": 9, "r10": 10, "r11": 11, "r12": 12, "r13": 13, "r14": 14,
    "r15": 15, "pc": 15
    }

# A complete DM2022 instruction word, in its decoded form.  In 
# memory an instruction is just an int.  Before executing an instruction,
# we decode it into an Instruction object so that we can more easily
# interpret its fields.

class Instruction(object):
    """An instruction is made up of several fields, 
       which are represented here as object fields."""
    
    def __init__(self, op: OpCode, cond: CondFlag,
                     reg_target: int, reg_src1: int,
                     reg_src2: int,
                     offset: int, 
                     reserved: int = 0): #Non-negotiable, always have to init
        """Assemble an instruction from its fields. """

        self.op = op
        self.cond =cond
        self.reg_target = reg_target
        self.reg_src1 = reg_src1
        self.reg_src2 = reg_src2
        self.offset = offset
        self.reserved = reserved
        return
    
    def __str__(self):
        """String representation looks something like assembly code"""
        if self.cond is CondFlag.ALWAYS:
            pred = ""
        else:
            pred = f'/{self.cond}'

        return (f"{self.op.name}{pred}{'   '}r{self.reg_target},r{self.reg_src1},r{self.reg_src2}[{self.offset}]")


def decode(word: int) -> Instruction:
    """Decode a memory word (32 bit int) into a new Instruction"""
    
    # Extract each value from the word
    reserved_value = reserved.extract(word)
    op_value = OpCode(op_field.extract(word))
    cond_value = CondFlag(cond_field.extract(word))
    reg_target_value = reg_target_field.extract(word)
    reg_src1_value = reg_src1_field.extract(word)
    reg_src2_value = reg_src2_field.extract(word)
    offset_value = offset_field.extract_signed(word)

    # Create an Instruction object using the extracted values
    instruction = Instruction(
        reserved=reserved_value,
        op=op_value,
        cond=cond_value,
        reg_target=reg_target_value,
        reg_src1=reg_src1_value,
        reg_src2=reg_src2_value,
        offset=offset_value
    )
    
    return instruction

def encode(self) -> int:

    #init the empty word
    word = 0

    #insert each field into the word
    word = op_field.insert(self.op.value, word)
    word = cond_field.insert(self.cond.value, word)
    word = reg_target_field.insert(self.reg_target, word)
    word = reg_src1_field.insert(self.reg_src1, word)
    word = reg_src2_field.insert(self.reg_src2, word)
    word = offset_field.insert(self.offset, word)  # Assuming you have a method to insert signed integers

    return word

#Add method to instruction class
Instruction.encode = encode




    



