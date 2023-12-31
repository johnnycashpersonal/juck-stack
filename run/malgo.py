"""Translate and run a mallard language program.
Top-level script chains together compiler, assembler phase 1,
assembler phase 2, and CPU simulator"""

import logging


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

log = logging.getLogger(__name__)

import io
import context
import compiler.compile as compile
import asm.assembler_phase1 as asm1
import asm.assembler_phase2 as asm2
import cpu.duck_machine as machine

import sys
import argparse
import os.path


def cli():
    """Get arguments from command line"""
    parser = argparse.ArgumentParser(description="Compile and go")
    parser.add_argument("sourcefile", type=argparse.FileType('r'),
                        nargs="?", default=sys.stdin,
                        help="Mallard source file")
    parser.add_argument("-d", "--display", help="Graphical display",
                        action="store_true")
    parser.add_argument("-s", "--step", help="Single step mode",
                        action="store_true")
    args = parser.parse_args()
    return args


def main(source: io.IOBase, display=False, step=False):
    # Create and use temporary files in ../programs/tmp
    this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    tmp_dir = os.path.abspath(os.path.join(this_dir, "../programs/tmp"))

    # Compiler
    asm_path = os.path.join(tmp_dir, "tmp.asm")
    asm_src = open(asm_path, "w")
    compile.main(source, asm_src)
    asm_src.close()

    # Assembler phase 1
    dasm_path = os.path.join(tmp_dir, "tmp.dasm")
    dasm = open(dasm_path, "w")
    asm_src = open(asm_path, "r")
    asm1.main(asm_src, dasm)
    dasm.close()

    # Assembler phase 2
    obj_path = os.path.join(tmp_dir, "tmp.obj")
    dasm = open(dasm_path, "r")
    obj = open(obj_path, "w")
    asm2.main(dasm, obj)
    obj.close()

    # Execute in simulator
    obj = open(obj_path, "r")
    machine.main(obj, display=display, single_step=step)


if __name__ == "__main__":
    args = cli()
    main(args.sourcefile, display=args.display, step=args.step)
