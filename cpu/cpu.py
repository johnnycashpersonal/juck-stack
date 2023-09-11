"""Duck Machine model DM2022 CPU - Revamped by JMo in 2023 Sept."""

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

    ALU_OPS = {
        OpCode.ADD: lambda x, y: x + y,
        OpCode.SUB: lambda x, y: x - y,
        OpCode.MUL: lambda x, y: x * y,
        OpCode.DIV: lambda x, y: x // y,
        OpCode.LOAD: lambda x, y: x + y,
        OpCode.STORE: lambda x, y: x + y,
        OpCode.HALT: lambda x, y: 0
    }
    
    def exec(self, op: OpCode, in1: int, in2: int) -> tuple[int, CondFlag]:
        try:
            result = self.ALU_OPS[op](in1, in2)
            
            if isinstance(result, ZeroDivisionError):
                raise result
            
        except ZeroDivisionError as zde:
            log.error(f"Caught an exception: {zde}")
            return 0, CondFlag.V
        except KeyError as ke:
            log.error(f"Invalid operation code: {op}")
            return 0, CondFlag.V

        if result == 0:
            return result, CondFlag.Z
        elif result < 0:
            return result, CondFlag.M
        else:
            return result, CondFlag.P

#note to self: It's not the ALU I Don't think. The ALU works.
class CPUStep(MVCEvent):
    """CPU is beginning step with PC at a given address"""
    def __init__(self, subject: "CPU", pc_addr: int,
                 instr_word: int, instr: Instruction)-> None:
        self.subject = subject
        self.pc_addr = pc_addr
        self.instr_word = instr_word
        self.instr = instr

#CPUStep is a direct copy.

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
        self.memory = memory 

        self.registers = [ZeroRegister(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register()]
        
        self.condition = CondFlag.ALWAYS
        self.halted = False
        self.alu = ALU()
        self.pc = self.registers[15]

        log.debug("CPU initialized with following register values:")
        for i, r in enumerate(self.registers):
            log.debug(f"Register {i}: {Register.get(r)}")
        
        #init, registers, condition is good

    def step(self):
        log.debug("Starting new CPU step")

        # Fetch Phase

        instr_addr = self.pc.get()  # Get the address from Register 15 (Program Counter)
        log.debug(f"Fetching instruction at address {instr_addr}")

        instr_word = self.memory.get(instr_addr)  # Get the instruction word from Memory
        log.debug(f"Fetched instruction word: {instr_word}")

        # Decode Phase

        instr = decode(instr_word)  # Decode the instruction word into an Instruction object
        log.debug(f"Decoded instruction: {instr}")

        # Display the CPU state when we have decoded the instruction, before executing it
        self.notify_all(CPUStep(self, instr_addr, instr_word, instr))
    
        # Execute Phase

        # Check the instruction predicate
        bitwise_result = self.condition & instr.cond
        if bitwise_result.value > 0:  # Condition is satisfied
            
            # Get operands
            left_operand = self.registers[instr.reg_src1].get()
            right_operand = instr.offset + self.registers[instr.reg_src2].get()
            
            # Call ALU
            result, new_condition = self.alu.exec(instr.op, left_operand, right_operand)
            
            # Increment Program Counter before saving results
            self.pc.put(self.pc.get() + 1)

            # Complete the operation based on OpCode
            if instr.op == OpCode.STORE:
                self.memory.put(result, self.registers[instr.reg_target].get())

            elif instr.op == OpCode.LOAD:
                load_value = self.memory.get(result)
                self.registers[instr.reg_target].put(load_value)

            elif instr.op == OpCode.HALT:
                self.halted = True

            else:  # For ADD, SUB, MUL, DIV
                self.registers[instr.reg_target].put(result)
                self.condition = new_condition

        else:
            # If condition not satisfied, increment Program Counter
            self.pc.put(self.pc.get() + 1)

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
        #The run method should be good, It's a direct copy


        