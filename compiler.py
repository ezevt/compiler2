from lparser import *
from dataclasses import *
from os import path


class Compiler:
	def __init__(self):
		self.start = True

	def visit(self, node, out):
		if self.start:
			self.start = False

			out.write("BITS 64\n")
			out.write("segment .text\n")
			out.write("print:\n")
			out.write("    mov     r9, -3689348814741910323\n")
			out.write("    sub     rsp, 40\n")
			out.write("    mov     BYTE [rsp+31], 10\n")
			out.write("    lea     rcx, [rsp+30]\n")
			out.write(".L2:\n")
			out.write("    mov     rax, rdi\n")
			out.write("    lea     r8, [rsp+32]\n")
			out.write("    mul     r9\n")
			out.write("    mov     rax, rdi\n")
			out.write("    sub     r8, rcx\n")
			out.write("    shr     rdx, 3\n")
			out.write("    lea     rsi, [rdx+rdx*4]\n")
			out.write("    add     rsi, rsi\n")
			out.write("    sub     rax, rsi\n")
			out.write("    add     eax, 48\n")
			out.write("    mov     BYTE [rcx], al\n")
			out.write("    mov     rax, rdi\n")
			out.write("    mov     rdi, rdx\n")
			out.write("    mov     rdx, rcx\n")
			out.write("    sub     rcx, 1\n")
			out.write("    cmp     rax, 9\n")
			out.write("    ja      .L2\n")
			out.write("    lea     rax, [rsp+32]\n")
			out.write("    mov     edi, 1\n")
			out.write("    sub     rdx, rax\n")
			out.write("    xor     eax, eax\n")
			out.write("    lea     rsi, [rsp+32+rdx]\n")
			out.write("    mov     rdx, r8\n")
			out.write("    mov     rax, 1\n")
			out.write("    syscall\n")
			out.write("    add     rsp, 40\n")
			out.write("    ret\n")
			out.write("global _start\n")
			out.write("_start:\n")

			method_name = f'visit_{type(node).__name__}'
			method = getattr(self, method_name, self.no_visit_method)
			method(node, out)

			out.write("    mov rax, 60\n")
			out.write("    mov rdi, 0\n")
			out.write("    syscall\n")
		else:
			method_name = f'visit_{type(node).__name__}'
			method = getattr(self, method_name, self.no_visit_method)
			return method(node, out)

	def no_visit_method(self, node, out):
		raise Exception(f'No visit_{type(node).__name__} method defined')
	
	def visit_NumberNode(self, node, out):
		out.write("    ;; -- push int %d --\n" % node.tok.value)
		out.write("    push rax, %d\n" % node.tok.value)
		return node.tok.value

	def visit_BinOpNode(self, node, out):
		self.visit(node.left_node, out)
		self.visit(node.right_node, out)

		if node.op_tok.type == TokenType.PLUS:
			out.write("    ;; -- plus --\n")
			out.write("    pop rax\n")
			out.write("    pop rbx\n")
			out.write("    add rax, rbx\n")
			out.write("    push rax\n")
		elif node.op_tok.type == TokenType.MINUS:
			out.write("    ;; -- minus --\n")
			out.write("    pop rax\n")
			out.write("    pop rbx\n")
			out.write("    add rax, rbx\n")
			out.write("    push rax\n")
		elif node.op_tok.type == TokenType.MUL:
			out.write("    ;; -- mul --\n")
			out.write("    pop rax\n")
			out.write("    pop rdx\n")
			out.write("    mul rdx\n")
			out.write("    push rax\n")

	def visit_UnaryOpNode(self, node, out):
		print("found UnaryOpNode")
		self.visit(node.node, out)
	
	def visit_PrintOpNode(self, node, out):
		self.visit(node.node, out)
		out.write("    ;; -- print --\n")
		out.write("    pop rdi\n")
		out.write("    call print\n")
