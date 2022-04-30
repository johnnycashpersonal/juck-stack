# duck-stack
The Duck Machine technology stack:  A CPU simulator, its assembler, and a compiler the language Mallard

This repository supports three projects in CIS 211 at University of Oregon. 

## Project 1:  A CPU simulator

In this project, a simulated CPU interprets Duck Machine instructions. Duck Machine machine
language instructions are encoded as 32 bit integers.  

Students will work in two subfolders

- instructions : The (binary) instruction encoding for Duck Machine processors
- cpu : The CPU simulator

## Project 2:  An assembler for Duck Machines

An assembler is a simple translator from an "assembly language" to a machine language. 
Each instruction line in assembly language is translated to a single machine instruction. 
There are two main tasks in translating assembly language to machine instructons: 

- Resolving adresses (e.g., determining the "target address" for a load, store, or jump instruction)
- Encoding instructions into the binary representation of the machine language

Most of the encoding is provided in "asm_encode".  Students are responsible for creating "asm_resolve", 
which implements the first task. 

## Project 3:  Mallard compiler

A compiler translates from a high level language like Python to a lower level language, often an
assembly language.  The higher language is called the "source language" and the lower level language
is called the "target language". Mallard is a high level language for Duck machines.
The source language for this compiler is Mallard, and the target language is Duck Machine 
assembly language. 

A compiler is typically composed of a "front end" that reads program source code and builds a tree
representation and a "back end" that translates the tree structure to the target language.  (Some 
compilers also have a "middle end" that analyzes and transforms the tree in various ways, but ours will not.) 
The front end is provided.  Students will build the back end. 


