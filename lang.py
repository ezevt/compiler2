from dataclasses import dataclass
from typing import *
import sys
import subprocess
import shlex
from compiler import *
from lparser import *
from lexer import *
from os import path

def cmd_call_echoed(cmd):
    print("[CMD] %s" % " ".join(map(shlex.quote, cmd)))
    return subprocess.call(cmd)


def usage(compiler_name):
    print("Usage: %s [OPTIONS] <SUBCOMMAND> [ARGS]" % compiler_name)
    print("  OPTIONS:")
    print("    -debug                Enable debug mode.")
    print("  SUBCOMMAND:")
    print("    com [OPTIONS] <file>  Compile the program")
    print("      OPTIONS:")
    print("        -r                  Run the program after successful compilation")
    print("        -o <file|dir>       Customize the output path")
    print("    help                  Print this help to stdout and exit with 0 code")

if __name__ == '__main__' and '__file__' in globals():
	argv = sys.argv
	# assert len(argv) >= 1
	compiler_name, *argv = argv

	while len(argv) > 0:
		if argv[0] == '-debug':
			debug = True
			argv = argv[1:]
		else:
			break

	if len(argv) < 1:
		usage(compiler_name)
		print("[ERROR] no subcommand is provided")
		exit(1)
	subcommand, *argv = argv

	if subcommand == "com":
		run = False
		program_path = None
		output_path = None
		while len(argv) > 0:
			arg, *argv = argv
			if arg == '-r':
				run = True
			elif arg == '-o':
				if len(argv) == 0:
					usage(compiler_name)
					print("[ERROR] no argument is provided for parameter -o")
					exit(1)
				output_path, *argv = argv
			else:
				program_path = arg
				break

		if program_path is None:
			usage(compiler_name)
			print("[ERROR] no input file is provided for the compilation")
			exit(1)

		basename = None
		basedir = None
		if output_path is not None:
			if path.isdir(output_path):
				basename = path.basename(program_path)
				lang_ext = '.lng'
				if basename.endswith(lang_ext):
					basename = basename[:-len(lang_ext)]
				basedir = path.dirname(output_path)
			else:
				basename = path.basename(output_path)
				basedir = path.dirname(output_path)
		else:
			basename = path.basename(program_path)
			lang_ext = '.lng'
			if basename.endswith(lang_ext):
				basename = basename[:-len(lang_ext)]
			basedir = path.dirname(program_path)
		basepath = path.join(basedir, basename)


		lexer = Lexer(basename, program_path)
		tokens, error = lexer.make_tokens()
		parser = Parser(tokens)
		ast = parser.parse()
		if ast.error:
			print(ast.error.as_string())
			exit(1)
		
		compiler = Compiler()
		with open(basepath + ".asm", "w") as out:
			compiler.visit(ast.node, out)

		cmd_call_echoed(["nasm", "-felf64", basepath + ".asm"])
		cmd_call_echoed(["ld", "-o", basepath, basepath + ".o"])
		if run:
			exit(cmd_call_echoed([basepath] + argv))
	elif subcommand == "help":
		usage(compiler_name)
		exit(0)
	else:
		usage(compiler_name)
		print("[ERROR] unknown subcommand %s" % (subcommand))
		exit(1)