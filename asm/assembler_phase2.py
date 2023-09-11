"""
Assembler Phase II for DM2022 assembly language.

This assembler is for fully resolved instructions,
which may be the output of assembler_phase1.py.

Assembly instruction format with all options is 

label: instruction

Labels are resolved (translated into addresses) in
phase I.  In fully resolved assembly code, the input
to this phase of the assembler, they serve
only as documentation.

Both parts are optional:  A label may appear without 
an instruction, and an instruction may appear without 
a label. 

A label is just an alphabetic string, eg.,
  myDogBoo but not Betcha_5_Dollars

An instruction has the following form: 

  opcode/predicate  target,src1,src2[disp]

Opcode is required, and should be one of the Duck Machine
instruction codes (ADD, MOVE, etc).

/predicate is optional.  If present, it should be some 
combination of M,Z,P, or V e.g., /NP would be "execute if
not zero".  If /predicate is not given, it is interpreted
as /ALWAYS, which is an alias for /MZPV.

target, src1, and src2 are register numbers (r0,r1, ... r15)

[disp] is optional.  If present, it is a 10 bit
signed integer displacement.  If absent, it is 
treated as [0]. 

DATA is a pseudo-operation:
   myvar:  DATA   18
indicates that the integer value 18
should be stored at this location, rather than
a Duck Machine instruction.

"""
import io

import context
from instruction_set.instr_format import Instruction, OpCode, CondFlag, NAMED_REGS

import argparse
from enum import Enum, auto
import sys
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Configuration constants
ERROR_LIMIT = 15    # Abandon assembly if we exceed this

# Exceptions raised by this module
class SyntaxError(Exception):
    pass

###
# The whole instruction line is encoded as a single
# regex with capture names for the parts we might
# refer to. Error messages will be crappy (we'll only
# know that the pattern didn't match, and not why), but 
# we get a very simple match/process cycle.  By creating
# a dict containing the captured fields, we can determine
# which optional parts are present (e.g., there could be
# label without an instruction or an instruction without
# a label).
###


# To simplify client code, we'd like to return a dict with
# the right fields even if the line is syntactically incorrect. 
DICT_NO_MATCH = { 'label': None, 'opcode': None, 'predicate': None,
                      'target': None, 'src1': None, 'src2': None,
                      'offset': None, 'comment': None }


###
# Although the Duck Machine instruction set is very simple, a source
# line can still come in several forms.  Each form (even comments)
# can start with a label.
###

class AsmSrcKind(Enum):
    """Distinguish which kind of assembly language instruction
    we have matched.  Each element of the enum corresponds to
    one of the regular expressions below.
    """
    # Blank or just a comment, optionally
    # with a label
    COMMENT = auto()
    # Fully specified  (all addresses resolved)
    FULL = auto()
    # A data location, not an instruction
    DATA = auto()


# Lines that contain only a comment (and possibly a label).
# This includes blank lines and labels on a line by themselves.
#
ASM_COMMENT_PAT = re.compile(r"""
   \s*
   # Optional label 
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   \s*
   # Optional comment follows # or ; 
   (
     (?P<comment>[\#;].*)
   )?       
   \s*$             
   """, re.VERBOSE)

# Instructions with fully specified fields. We can generate
# code directly from these.
ASM_FULL_PAT = re.compile(r"""
   \s*
   # Optional label 
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   \s*
    # The instruction proper 
    (?P<opcode>    [a-zA-Z]+)           # Opcode
    (/ (?P<predicate> [A-Z]+) )?   # Predicate (optional)
    \s+
    (?P<target>    r[0-9]+),            # Target register
    (?P<src1>      r[0-9]+),            # Source register 1
    (?P<src2>      r[0-9]+)             # Source register 2
    (\[ (?P<offset>[-]?[0-9]+) \])?     # Offset (optional)
   # Optional comment follows # or ; 
   (
     \s*
     (?P<comment>[\#;].*)
   )?       
   \s*$             
   """, re.VERBOSE)

# Defaults for values that ASM_FULL_PAT makes optional
INSTR_DEFAULTS = [ ('predicate', 'ALWAYS'), ('offset', '0') ]

# A data word in memory; not a Duck Machine instruction
#
ASM_DATA_PAT = re.compile(r""" 
   \s* 
   # Optional label 
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   # The instruction proper  
   \s*
    (?P<opcode>    DATA)           # Opcode
   # Optional data value
   \s*
   (?P<value>  (0x[a-fA-F0-9]+)
             | ([0-9]+))?
    # Optional comment follows # or ; 
   (
     \s*
     (?P<comment>[\#;].*)
   )?       
   \s*$             
   """, re.VERBOSE)


# We will try each pattern in turn.  The PATTERNS table
# is to associate each pattern with the kind of instruction
# that each pattern matches.
#
PATTERNS = [(ASM_FULL_PAT, AsmSrcKind.FULL),
            (ASM_DATA_PAT, AsmSrcKind.DATA),
            (ASM_COMMENT_PAT, AsmSrcKind.COMMENT)
            ]

def parse_line(line: str) -> dict:
    """Parse one line of assembly code."""
    log.debug(f"Starting to parse assembler line: '{line.strip()}'")
    
    for pattern, kind in PATTERNS:
        match = pattern.fullmatch(line)
        if match:
            fields = match.groupdict()
            fields["kind"] = kind
          #  log.debug(f"Successfully parsed line with kind '{kind}'. Extracted fields: {fields}")
            return fields
    
  #  log.error(f"Failed to parse line: '{line.strip()}'. Syntax does not match any known patterns.")
    raise SyntaxError(f"Assembler syntax error in {line.strip()}")

def fill_defaults(fields: dict) -> None:
    """Fill in default values for optional fields of instruction."""
   # log.debug(f"Filling default values for fields: {fields}")
    for key, value in INSTR_DEFAULTS:
        if fields[key] == None:
            fields[key] = value
            log.debug(f"Filled default value for {key}: {value}")

def value_parse(int_literal: str) -> int:
    """Parse an integer literal that could look like 42 or like 0x2a."""
    if int_literal.startswith("0x"):
        value = int(int_literal, 16)
      #  log.debug(f"Integer literal is in hexadecimal. Parsed value: {value}")
        return value
    else:
        value = int(int_literal, 10)
       # log.debug(f"Integer literal is in decimal. Parsed value: {value}")
        return value

def to_flag(m: str) -> CondFlag:
    """Making a condition code from a mnemonic."""
    # Check if the mnemonic directly matches a predefined condition flag
    if m in CondFlag.__members__:
      #  log.debug(f"Mnemonic matches a predefined condition flag.")
        return CondFlag[m]

    # Handle composite condition flags
    composite = CondFlag.NEVER
    for bitname in m:
      #  log.debug(f"Processing bitname: {bitname}")  # Log each bitname being processed

        if bitname in CondFlag.__members__:
            composite = composite | CondFlag[bitname]
        else:
            raise KeyError(f"Invalid bitname in mnemonic: {bitname}")
        
   # log.debug(f"Constructed composite condition flag: {composite}")
    return composite



def instruction_from_dict(d: dict) -> Instruction:
    """Use fields of d to create an Instruction object."""
    log.debug(f"Constructing instruction from fields: {d}")
    try:
        opcode = OpCode[d["opcode"]]
        pred = to_flag(d["predicate"])
        target = NAMED_REGS[d["target"]]
        src1 = NAMED_REGS[d["src1"]]
        src2 = NAMED_REGS[d["src2"]]
        offset = int(d["offset"])
        
       # log.debug(f"Constructed instruction with opcode: {opcode}, predicate: {pred}, target: {target}, src1: {src1}, src2: {src2}, offset: {offset}")
        return Instruction(opcode, pred, target, src1, src2, offset)
    except KeyError as e:
        log.error(f"KeyError: Missing or misspelled field in dictionary: {e}")
        raise

def assemble(lines: list[str]) -> list[int]:
    """
    Simple one-pass translation of assembly language source code into instructions.
    """
    error_count = 0
    instructions = []

    for lnum, line in enumerate(lines):
      #  log.debug(f"Processing line {lnum}: {line.strip()}")
        
        try:
            fields = parse_line(line)
            if fields["kind"] == AsmSrcKind.FULL:
               # log.debug("Constructing FULL instruction")
                fill_defaults(fields)
                instr = instruction_from_dict(fields)
                word = instr.encode()
                instructions.append(word)
                log.debug(f"FULL instruction encoded: {word}")

            elif fields["kind"] == AsmSrcKind.DATA:
             #   log.debug("Constructing DATA instruction")
                word = value_parse(fields["value"])
                instructions.append(word)
                log.debug(f"DATA instruction encoded: {word}")

            else:
                log.debug(f"No instruction on line {lnum}. Skipping.")

        except SyntaxError as e:
            error_count += 1
            log.error(f"Syntax error in line {lnum}: {e}")
        
        except KeyError as e:
            error_count += 1
            log.error(f"Unknown word in line {lnum}: {e}")

        except Exception as e:
            error_count += 1
            log.error(f"Unexpected exception in line {lnum}: {e}")

        if error_count > ERROR_LIMIT:
            log.critical("Too many errors; abandoning assembly.")
            sys.exit(1)

    log.debug(f"Assembly complete. {len(instructions)} instructions generated.")
    return instructions

def cli() -> object:
    """Get arguments from command line"""
    parser = argparse.ArgumentParser(description="Duck Machine Assembler (pass 2)")
    parser.add_argument("sourcefile", type=argparse.FileType('r'),
                            nargs="?", default=sys.stdin,
                            help="Duck Machine assembly code file")
    parser.add_argument("objfile", type=argparse.FileType('w'),
                            nargs="?", default=sys.stdout, 
                            help="Object file output")
    args = parser.parse_args()
    return args


def main(sourcefile: io.IOBase, objfile: io.IOBase):
    """"Assemble a Duck Machine program"""
    lines = sourcefile.readlines()
    object_code = assemble(lines)
  #  log.debug(f"Object code: \n{object_code}")
    for word in object_code:
        log.debug(f"Instruction word {word}")
        print(word,file=objfile)

if __name__ == "__main__":
    args = cli()
    main(args.sourcefile, args.objfile)

