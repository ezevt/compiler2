BITS 64
segment .text
print:
    mov     r9, -3689348814741910323
    sub     rsp, 40
    mov     BYTE [rsp+31], 10
    lea     rcx, [rsp+30]
.L2:
    mov     rax, rdi
    lea     r8, [rsp+32]
    mul     r9
    mov     rax, rdi
    sub     r8, rcx
    shr     rdx, 3
    lea     rsi, [rdx+rdx*4]
    add     rsi, rsi
    sub     rax, rsi
    add     eax, 48
    mov     BYTE [rcx], al
    mov     rax, rdi
    mov     rdi, rdx
    mov     rdx, rcx
    sub     rcx, 1
    cmp     rax, 9
    ja      .L2
    lea     rax, [rsp+32]
    mov     edi, 1
    sub     rdx, rax
    xor     eax, eax
    lea     rsi, [rsp+32+rdx]
    mov     rdx, r8
    mov     rax, 1
    syscall
    add     rsp, 40
    ret
global _start
_start:
    ;; -- push int 2 --
    push rax, 2
    ;; -- push int 4 --
    push rax, 4
    ;; -- mul --
    pop rax
    pop rdx
    mul rdx
    push rax
    ;; -- push int 1 --
    push rax, 1
    ;; -- plus --
    pop rax
    pop rbx
    add rax, rbx
    push rax
    ;; -- print --
    pop rdi
    call print
    mov rax, 60
    mov rdi, 0
    syscall
