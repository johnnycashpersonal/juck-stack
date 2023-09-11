"""Test cases for the binary encoding of 
instructions. 
"""

import context
from instruction_set.instr_format import *
import unittest

class TestCondCodes(unittest.TestCase):
    """Condition flags are essentially like single bit bitfields"""

    def test_combine_flags(self):
        non_zero = CondFlag.P | CondFlag.M
        self.assertEqual(str(non_zero), "MP")
        positive = CondFlag.P
        self.assertEqual(str(positive), "P")
        self.assertEqual(str(CondFlag.ALWAYS), "ALWAYS")
        self.assertEqual(str(CondFlag.NEVER), "NEVER")
        # We test overlap of two CondFlag values using bitwise AND
        self.assertTrue(positive & non_zero)
        zero = CondFlag.Z
        self.assertFalse(zero & non_zero)

class TestInstructionString(unittest.TestCase):
    """Check that we can print Instruction objects like assembly language"""

    def test_str_predicated_MUL(self):
        instr = Instruction(OpCode.MUL, CondFlag.P | CondFlag.Z,
                        NAMED_REGS["r1"], NAMED_REGS["r3"], NAMED_REGS["pc"], 42)
        self.assertEqual("MUL/ZP   r1,r3,r15[42]", str(instr))
        print(instr)

    def test_str_always_ADD(self):
        """Predication is not printed for the common value of ALWAYS"""
        instr = Instruction(OpCode.ADD, CondFlag.ALWAYS,
                            NAMED_REGS["zero"], NAMED_REGS["pc"], NAMED_REGS["r15"], 0)
        self.assertEqual("ADD   r0,r15,r15[0]", str(instr))
        print(instr)

class TestDecode(unittest.TestCase):
    """Encoding and decoding should be inverses"""
    def test_encode_decode(self):
        instr = Instruction(OpCode.SUB, CondFlag.M | CondFlag.Z, NAMED_REGS["r2"], NAMED_REGS["r1"], NAMED_REGS["r3"], -12)
        word = instr.encode()
        text = str(decode(word))
        self.assertEqual(text, str(instr))

        print(text)

class TestEdgeCasesForCondFlags(unittest.TestCase):
    def test_all_flags(self):
        all_flags = CondFlag.M | CondFlag.Z | CondFlag.P | CondFlag.V
        self.assertEqual(str(all_flags), "ALWAYS")

    def test_no_flags(self):
        no_flags = CondFlag.NEVER
        self.assertEqual(str(no_flags), "NEVER")


class TestRegisterBoundaries(unittest.TestCase):
    def test_lowest_and_highest_register(self):
        instr_low = Instruction(OpCode.ADD, CondFlag.ALWAYS, NAMED_REGS["r0"], NAMED_REGS["r1"], NAMED_REGS["r2"], 0)
        instr_high = Instruction(OpCode.ADD, CondFlag.ALWAYS, NAMED_REGS["r15"], NAMED_REGS["r14"], NAMED_REGS["r13"], 0)
        
        self.assertEqual("ADD   r0,r1,r2[0]", str(instr_low))
        self.assertEqual("ADD   r15,r14,r13[0]", str(instr_high))


class TestOffsetBoundaries(unittest.TestCase):
    def test_max_min_offset(self):
        instr_max = Instruction(OpCode.ADD, CondFlag.ALWAYS, NAMED_REGS["r1"], NAMED_REGS["r2"], NAMED_REGS["r3"], 2**11 - 1)
        instr_min = Instruction(OpCode.ADD, CondFlag.ALWAYS, NAMED_REGS["r1"], NAMED_REGS["r2"], NAMED_REGS["r3"], -(2**11))
        
        self.assertTrue("ADD   r1,r2,r3[2047]" in str(instr_max))
        self.assertTrue("ADD   r1,r2,r3[-2048]" in str(instr_min))


class TestEncodeDecodeAllOpCodes(unittest.TestCase):
    def test_all_opcodes(self):
        for op in OpCode:
            instr = Instruction(op, CondFlag.ALWAYS, NAMED_REGS["r1"], NAMED_REGS["r2"], NAMED_REGS["r3"], 0)
            word = instr.encode()
            decoded_instr = decode(word)
            
            self.assertEqual(str(decoded_instr), str(instr))


class TestReservedField(unittest.TestCase):
    def test_reserved_field(self):
        instr = Instruction(OpCode.ADD, CondFlag.ALWAYS, NAMED_REGS["r1"], NAMED_REGS["r2"], NAMED_REGS["r3"], 0, reserved=1)
        word = instr.encode()
        decoded_instr = decode(word)
        
        self.assertEqual(str(decoded_instr), str(instr))
        self.assertEqual(decoded_instr.reserved, 0)  # Should always be zero

if __name__ == "__main__":
    unittest.main()
