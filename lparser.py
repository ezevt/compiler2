from ast import expr
from asyncio import current_task
from importlib.util import module_from_spec
from lexer import *

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class PrintOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

class VarReAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

class ListNode:
	def __init__(self, element_nodes):
		self.element_nodes = element_nodes

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register_advancement(self):
		pass

	def register(self, res):
		if res.error: self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.statements()
		if not res.error and self.current_tok.type != TokenType.EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	###################################

	def statements(self):
		res = ParseResult()
		statements = []

		while self.current_tok.type == TokenType.NEWLINE:
			self.advance()
		
		statement = res.register(self.statement())
		if res.error: return res
		statements.append(statement)

		more_statements = True

		while True:
			newline_count = 0
			while self.current_tok.type == TokenType.NEWLINE:
				self.advance()
				newline_count += 1
			if newline_count == 0:
				more_statements = False
			
			if not more_statements: break
			statement = res.register(self.statement())
			if res.error:
				more_statements = False
				continue
			statements.append(statement)

		return res.success(ListNode(statements))				

	def statement(self):
		res = ParseResult()

		if self.current_tok.matches(TokenType.TYPE, 'int'):
			res.register_advancement()
			self.advance()
			
			if self.current_tok.type != TokenType.IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier"
				))
			
			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TokenType.EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))
			
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())

			if res.error: return res
			return res.success(VarAssignNode(var_name, expr))
		if self.current_tok.matches(TokenType.KEYWORD, 'print'):
			tok = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TokenType.LPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '('"
				))
			
			res.register_advancement()
			self.advance()
			
			expr = res.register(self.expr())

			if self.current_tok.type != TokenType.RPAREN:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

			res.register_advancement()
			self.advance()

			if res.error: return res
			return res.success(PrintOpNode(tok, expr))
		return self.expr()

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TokenType.PLUS, TokenType.MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.type == TokenType.INT:
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == TokenType.IDENTIFIER:
			res.register_advancement()
			self.advance()
			if self.current_tok.type == TokenType.EQ:
				res.register_advancement()
				self.advance()

				expr = res.register(self.expr())
				if res.error: return res

				return res.success(VarReAssignNode(tok, expr))
			else:
				return res.success(VarAccessNode(tok))

		elif tok.type == TokenType.LPAREN:
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TokenType.RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

	def term(self):
		return self.bin_op(self.factor, (TokenType.MUL, TokenType.DIV))

	def expr(self):
		return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

	###################################

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)