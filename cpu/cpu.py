"""
Duck Machine model DM2022 CPU
"""

import context  #  Python import search from project root
from instruction_set.instr_format import Instruction, OpCode, CondFlag, decode
from cpu.memory import Memory
from cpu.register import Register, ZeroRegister
from cpu.mvc import MVCEvent, MVCListenable

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ALU(object):
    """The arithmetic logic unit (also called a "functional unit"
    in a modern CPU) executes a selected function but does not
    otherwise manage CPU state. A modern CPU core may have several
    ALUs to boost performance by performing multiple operatons
    in parallel, but the Duck Machine has just one ALU in one core.
    """
    # The ALU chooses one operation to apply based on a provided
    # operation code.  These are just simple functions of two arguments;
    # in hardware we would use a multiplexer circuit to connect the
    # inputs and output to the selected circuitry for each operation.
    
    ALU_OPS = {
        OpCode.ADD: lambda x, y: x + y,
        OpCode.SUB: lambda x, y: x - y,
        OpCode.MUL: lambda x, y: x * y,
        OpCode.DIV: lambda x, y: x // y,
        
        # For memory access operations load, store, the ALU performs the address calculation
        OpCode.LOAD: lambda x, y: x + y,
        OpCode.STORE: lambda x, y: x + y,
        # Some operations perform no operation
        OpCode.HALT: lambda x, y: 0
    }

    def exec(self, op: OpCode, in1: int, in2: int) -> tuple[int, CondFlag]:
        try:
            #Lookup the opcode associated with the function and execute it
            result = self.ALU_OPS[op](in1,in2)
        except Exception as e:
            #Handle Exceptions like DIV 0
            return 0, CondFlag.V
        
        #Condition flag, based on result
        if result == 0:
            return result, CondFlag.Z
        elif result < 0:
            return result, CondFlag.M
        else: 
            return result, CondFlag.P

            #M Indicates the result is negative
            #Z indicates the result of an operation is 0
            #P indicates the result of something is positive
            #V indicates an arithmatic overflow like div0 has occurred

            #NEVER and ALWAYS indicate something should be always or never true

class CPUStep(MVCEvent):
    """CPU is beginning step with PC at a given address"""
    def __init__(self, subject: "CPU", pc_addr: int,
                 instr_word: int, instr: Instruction)-> None:
        self.subject = subject
        self.pc_addr = pc_addr
        self.instr_word = instr_word
        self.instr = instr
             