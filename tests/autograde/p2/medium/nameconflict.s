.globl main
main:
	pushl %ebp ## save caller's base pointer 
	movl %esp, %ebp ## set our base pointer 
	subl $4, %esp ## allocate for local vars
	pushl %ebx ## save callee saved registers
	pushl %esi
	pushl %edi
	ENTRY_0:
	
STATEMENT_1:
	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $0
	call inject_int
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %ebx, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call create_list
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %ebx, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call inject_big
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	pushl $closure_0
	call create_closure
	movl %eax, %ebx
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $1
	call inject_int
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %edi, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call create_list
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %edi, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call inject_big
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $0
	call inject_int
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %esi, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	pushl %eax
	pushl %edi
	call set_subscript
	addl $12, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	pushl $closure_1
	call create_closure
	movl %eax, %ebx
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $0
	call inject_int
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %edi, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call create_list
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %edi, %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	call inject_big
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	pushl $closure_2
	call create_closure
	movl %eax, %edi
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call inject_big
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %esi
	call get_free_vars
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call inject_big
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call get_fun_ptr
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $2
	call inject_int
	movl %eax, -4(%ebp)
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl -4(%ebp), %eax

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %eax
	pushl %esi
	call *%edi
	movl %eax, %edi
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call print_any
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call inject_big
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call get_free_vars
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call inject_big
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call get_fun_ptr
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call *%ebx
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %esi
	call inject_big
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %esi
	call get_free_vars
	movl %eax, %esi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	call *%ebx
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call inject_big
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call get_fun_ptr
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $4
	call inject_int
	movl %eax, %edi
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %edi
	pushl %esi
	call *%ebx
	movl %eax, %ebx
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	call print_any
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers
EXIT_2:
	

popl %edi ## restore callee saved registers
	popl %esi
	popl %ebx
	movl $0, %eax ## set return value 
	movl %ebp, %esp ## restore esp
	popl %ebp ## restore ebp (alt. “leave”)
	ret ## jump execution to call site

closure_2:
	pushl %ebp ## save caller's base pointer 
	movl %esp, %ebp ## set our base pointer 
	subl $0, %esp ## allocate for local vars
	pushl %ebx ## save callee saved registers
	pushl %esi
	pushl %edi
	movl 12(%ebp), %eax
	ENTRY_3:
	
STATEMENT_4:
	movl %eax, %eax
	popl %edi ## restore callee saved registers
	popl %esi
	popl %ebx
	movl %ebp, %esp ## restore esp
	popl %ebp ## restore ebp
	ret
EXIT_5:
	


closure_1:
	pushl %ebp ## save caller's base pointer 
	movl %esp, %ebp ## set our base pointer 
	subl $0, %esp ## allocate for local vars
	pushl %ebx ## save callee saved registers
	pushl %esi
	pushl %edi
	movl 8(%ebp), %edi
	ENTRY_6:
	
STATEMENT_7:
	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl $0
	call inject_int
	movl %eax, %ebx
	addl $4, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	pushl %eax ## save caller-saved registers
	pushl %ecx ## save caller-saved registers
	pushl %edx ## save caller-saved registers
	pushl %ebx
	pushl %edi
	call get_subscript
	movl %eax, %ebx
	addl $8, %esp
	popl %edx ## restore caller-saved registers
	popl %ecx ## restore caller-saved registers
	popl %eax ## restore caller-saved registers

	movl %ebx, %eax
	popl %edi ## restore callee saved registers
	popl %esi
	popl %ebx
	movl %ebp, %esp ## restore esp
	popl %ebp ## restore ebp
	ret
EXIT_8:
	


closure_0:
	pushl %ebp ## save caller's base pointer 
	movl %esp, %ebp ## set our base pointer 
	subl $0, %esp ## allocate for local vars
	pushl %ebx ## save callee saved registers
	pushl %esi
	pushl %edi
	movl 12(%ebp), %eax
	ENTRY_9:
	
STATEMENT_10:
	movl %eax, %eax
	popl %edi ## restore callee saved registers
	popl %esi
	popl %ebx
	movl %ebp, %esp ## restore esp
	popl %ebp ## restore ebp
	ret
EXIT_11:
	

