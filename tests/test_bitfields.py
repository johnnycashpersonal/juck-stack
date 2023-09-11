"""Unit tests for bitfield.py"""
import os
import unittest
import context
from instruction_set.bitfield import BitField

class Test_Extract(unittest.TestCase):

    def test_extract_low(self):
        """Extract low 3 bits"""
        low_bits = BitField(0,3)
        self.assertEqual(low_bits.extract(0b10101010101), 0b101)

    def test_middle_bits(self):
        """Extract 5 bits from the middle of a word"""
        middle_bits = BitField(5,9)
        self.assertEqual(middle_bits.extract(0b1010101101101011), 0b11011)

class Test_Insert(unittest.TestCase):
    def test_insert_low(self):
        """Inserting a few bits in the lowest part of the word. """
        low_bits = BitField(0,3)
        self.assertEqual(low_bits.insert(15,0), 15)  # All the bits to 1
        
        # Slip it in without disturbing higher bits
        self.assertEqual(low_bits.insert(0b1010, 0b1111_0000), 0b1111_1010)

class Test_Sign_Extension(unittest.TestCase):

    def test_extend_positive(self):
        """Sign extension of a positive number doesn't change it.  Note high
        bit in field must be zero.  7 is a positive number in a 3-bit field,
        but a (different) negative number in a 3-bit field.
        """
        self.assertEqual(BitField.sign_extend(7,4), 7)
        self.assertNotEqual(BitField.sign_extend(7,3), 7)
        self.assertTrue(BitField.sign_extend(7,3) < 0)

    def test_extend_negative(self):
        """For negative numbers, sign extension restores the high bits"""
        chunk = (-3) & 0b111
        self.assertEqual(BitField.sign_extend(chunk,3), -3)
    
class Test_Signed_Extraction(unittest.TestCase):

    def test_extract_neg(self):
        bitfield = BitField(2,4)
        field_bits = 0b_101_111_10  # the 111 part is what we want to extract
        self.assertEqual(bitfield.extract_signed(field_bits), -1)

    def test_extract_pos(self):
        bitfield = BitField(2,4)
        field_bits = 0b_101_011_10  # the 011 part is what we want to extract
        self.assertEqual(bitfield.extract_signed(field_bits), 3)  

class Test_Signed_Insert(unittest.TestCase):

    def test_insert_neg(self):
        bitfield = BitField(3,5)
        packed = bitfield.insert(-1, 0)
        self.assertEqual(packed, 0b000_111_000)
        unpacked = bitfield.extract_signed(packed)
        self.assertEqual(unpacked, -1)

import unittest
from instruction_set.bitfield import BitField

class TestExtremeWordValues(unittest.TestCase):
    
    def test_max_min_word(self):
        bf = BitField(0, 31)
        self.assertEqual(bf.extract(0xFFFFFFFF), 0xFFFFFFFF)  # All bits set
        self.assertEqual(bf.extract(0x80000000), 0x80000000)  # Only the sign bit set
        self.assertEqual(bf.extract(0x7FFFFFFF), 0x7FFFFFFF)  # All but the sign bit set

class TestInvalidInput(unittest.TestCase):
    
    def test_negative_from_bit(self):
        with self.assertRaises(AssertionError):
            BitField(-1, 5)
            
    def test_negative_to_bit(self):
        with self.assertRaises(AssertionError):
            BitField(1, -5)
            
    def test_from_greater_than_to(self):
        with self.assertRaises(AssertionError):
            BitField(10, 5)
            
class TestExtractAllBits(unittest.TestCase):
    
    def test_extract_all(self):
        bf = BitField(0, 31)
        self.assertEqual(bf.extract(0x12345678), 0x12345678)

class TestInsertAllBits(unittest.TestCase):
    
    def test_insert_all(self):
        bf = BitField(0, 31)
        self.assertEqual(bf.insert(0x12345678, 0xFFFFFFFF), 0x12345678)

class TestSignExtensionEdgeCases(unittest.TestCase):
    
    def test_min_max_negative(self):
        self.assertEqual(BitField.sign_extend(0b11111111, 8), -1)
        self.assertEqual(BitField.sign_extend(0b10000000, 8), -128)

    def test_min_max_positive(self):
        self.assertEqual(BitField.sign_extend(0b00000001, 8), 1)
        self.assertEqual(BitField.sign_extend(0b01111111, 8), 127)

if __name__ == '__main__':
    unittest.main()


if __name__ == "__main__":
    print(os.getcwd())
    unittest.main()