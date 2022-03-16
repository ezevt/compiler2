from dataclasses import dataclass
from enum import Enum, auto
from locale import currency
from typing import *
import sys
from strings_with_arrows import *
from os import path

Loc=Tuple[str, int, int]
DIGITS='0123456789'

class TokenType(Enum):
	PLUS=auto()
	MINUS=auto()
	MUL=auto()
	DIV=auto()
	INT=auto()
	LPAREN=auto()
	RPAREN=auto()
	EOF=auto()

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
		
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class Token:
		def __init__(self, type_, value=None, pos_start=None, pos_end=None):
			self.type = type_
			self.value = value

			if pos_start:
				self.pos_start = pos_start.copy()
				self.pos_end = pos_start.copy()
				self.pos_end.advance()

			if pos_end:
				self.pos_end = pos_end
		
		def __repr__(self):
			if self.value: return f'{self.type}:{self.value}'
			return f'{self.type}'

class Lexer:
		def __init__(self, fn, file_path):
			with open(file_path, "r") as f:
				self.text = f.read()
			self.fn = fn
			self.pos = Position(-1, 0, -1, fn, self.text)
			self.current_char = None
			self.advance()
		
		def advance(self):
			self.pos.advance(self.current_char)
			self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

		def make_tokens(self):
			tokens = []
			while self.current_char != None:
				if self.current_char in ' \t':
					self.advance()
				elif self.current_char in DIGITS:
					tokens.append(self.make_number())
				elif self.current_char == '+':
					tokens.append(Token(TokenType.PLUS, pos_start=self.pos))
					self.advance()
				elif self.current_char == '-':
					tokens.append(Token(TokenType.MINUS, pos_start=self.pos))
					self.advance()
				elif self.current_char == '*':
					tokens.append(Token(TokenType.MUL, pos_start=self.pos))
					self.advance()
				elif self.current_char == '/':
					tokens.append(Token(TokenType.DIV, pos_start=self.pos))
				elif self.current_char == '(':
					tokens.append(Token(TokenType.LPAREN, pos_start=self.pos))
					self.advance()
				elif self.current_char == ')':
					tokens.append(Token(TokenType.RPAREN, pos_start=self.pos))
					self.advance()
				else:
					pos_start = self.pos.copy()
					char = self.current_char
					self.advance()
					return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
			tokens.append(Token(TokenType.EOF, pos_start=self.pos))
			return tokens, None

		def make_number(self):
			num_str = ''
			dot_count = 0
			pos_start = self.pos.copy()

			while self.current_char != None and self.current_char in DIGITS + '.':
				if self.current_char == '.':
					if dot_count == 1: break
					dot_count += 1
					num_str += '.'
				else:
						num_str += self.current_char
				self.advance()
			
			if dot_count == 0:
				return Token(TokenType.INT, int(num_str), pos_start, self.pos)
			else:
				assert False
	


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

# TODO: there is no way to access command line arguments

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
		print(lexer.make_tokens())

		# print("[INFO] Generating %s" % (basepath + ".asm"))
		# program = load_program_from_file(program_path)
		# compile_program(program, basepath + ".asm")
		# cmd_call_echoed(["nasm", "-felf64", basepath + ".asm"])
		# cmd_call_echoed(["ld", "-o", basepath, basepath + ".o"])
		# if run:
		# 	exit(cmd_call_echoed([basepath] + argv))
	elif subcommand == "help":
		usage(compiler_name)
		exit(0)
	else:
		usage(compiler_name)
		print("[ERROR] unknown subcommand %s" % (subcommand))
		exit(1)