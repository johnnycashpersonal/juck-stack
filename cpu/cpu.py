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

class CPU(MVCListenable):
    """Duck Machine central processing unit (CPU)
    has 16 registers (including r0 that always holds zero
    and r15 that holds the program counter), a few
    flag registers (condition codes, halted state),
    and some logic for sequencing execution.  The CPU
    does not contain the main memory but has a bus connecting
    it to a separate memory.
    """
    def __init__(self, memory: Memory):
        super().__init__()
        self.memory = memory #This is not actually a part of the cpu, but a connection
        self.registers = [ZeroRegister(), Register(), Register(), Register(),
                              Register(), Register(), Register(), Register(),
                              Register(), Register(), Register(), Register(),
                              Register(), Register(), Register(), Register()]
        
        self.condition = CondFlag.ALWAYS
        self.halted = False
        self.alu = ALU()
        self.pc = self.registers[15]
    
    def step(self):
        """One fetch/execute/decode step"""

        #FETCH PHASE
        instr_addr = Register.get(self.pc)

        instr_word = self.memory.get(instr_addr)

        #DECODE PHASE
        instr = decode(instr_word)

        # Display the CPU state when we have decoded the instruction,
        # before we have executed it
        self.notify_all(CPUStep(self, instr_addr, instr_word, instr))
        
        #CHECK PREDICATE
        condition_satisfied = False 

        #Perform bitwise AND between CPU condition and instruction condition field
        bitwise_result = self.condition & instr.cond
        bitwise_result_value = bitwise_result.value

        #Execute based on if Bitwise AND is positive
        if bitwise_result_value > 0:
            condition_satisfied = True
        
        #Now we proceed, else, kill
        if condition_satisfied:

    #Grab the left operand from register stored in instr.src1
            left_operand = Register.get(self.registers[instr.reg_src1])

    #Grab the right operand
            right_operand = instr.offset + Register.get(self.registers[instr.reg_src2])

    #Execute ALU Operation
            result, new_condition = self.alu.exec(instr.op, left_operand, right_operand)

    #BEFORE SAVING RESULT AND COND CODE, Implement Program Counter
            self.pc.put(Register.get(self.pc) + 1)
            
    #We now have to complete the OpCode-Based Logic.
            
            if instr.op == OpCode.STORE:
                #Store value into memory at calculated address (result)
                self.memory.put(result, Register.get(self.registers[instr.reg_target]))
            
            elif instr.op == OpCode.LOAD:
                # Load the value from memory at the calculated address (result)
                load_value = self.memory.get(result)
                self.registers[instr.reg_target].put(load_value)

            elif instr.op == OpCode.HALT:
                #Set the halt flag
                self.halted = True
            
            else:
                #For ADD, SUB, MUL, DIV, Store the result in the target register
                self.registers[instr.reg_target].put(result)
                #Update the condition code
                self.condition = new_condition

        else:
            #If the condition is not satisfied, just increment the program counter
            self.pc.put(Register.get(self.pc) + 1)

    def run(self, from_addr=0,  single_step=False) -> None:
        """Step the CPU until it executes a HALT"""
        self.halted = False
        self.registers[15].put(from_addr)
        step_count = 0
        while not self.halted:
            if single_step:
                input(f"Step {step_count}; press enter")
            self.step()
            step_count += 1


