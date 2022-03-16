from error import *
from enum import Enum, auto
from position import *

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
