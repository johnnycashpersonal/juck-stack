"""instr_format.py will contain definitions of the fields in the DM2022 instruction word, and a class Instruction to hold a "decoded" instruction. 
An Instruction object will simply have a separate field (instance variable) for each of the fields in a DM2022 instruction word, plus methods to convert between words (integers) and Instruction objects. 
While the CPU decodes instructions, we will also need to encode them with the assembler we will build next week. 
Since the assembler and CPU need consistent definitions of the instruction format, instr_format.py is in the separate instruction_set directory, along with the BitField class."""