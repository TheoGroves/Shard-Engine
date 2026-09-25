default rel

section .data
    ; store 0.5 and 1.5 for newton-raphson 
    const_0_5: dd 0.5
    const_1_5: dd 1.5

    ; store conversion factors for degree-radian conversion
    const_deg2rad: dd 0.017453292519943295
    const_rad2deg: dd 57.29577951308232

    ; mask to zero w component
    cross_mask: dd 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000000

section .bss

section .text
    global vec4_add
    global vec4_sub
    global vec4_mul_s
    global vec4_div_s
    global vec4_dot
    global vec4_cross
    global vec4_length
    global vec4_normalize
    global vec4_minimum
    global vec4_maximum
    global vec4_round
    global vec4_radians
    global vec4_degrees

; compile-time macro replaces all instances of load_xmm with code
%macro load_xmm 0
    movaps xmm0, [rcx]
    movaps xmm1, [rdx]
%endmacro

; 1st = rcx, 2nd = rdx
vec4_add:
    ; move all terms into xmm registers
    load_xmm

    ; add all terms at once
    vaddps xmm2, xmm0, xmm1
    
    movaps [r8], xmm2
    ret

vec4_sub:
    ; move all terms into xmm registers
    load_xmm

    ; subtract all terms at once
    vsubps xmm2, xmm0, xmm1

    movaps [r8], xmm2
    ret

; scalar multiplication
vec4_mul_s:
    movaps xmm0, [rcx]
    movss xmm1, [rdx]
    shufps xmm1, xmm1, 0x00 ; shuffles term 0 into terms 0 1 2 and 3

    ; multiply all terms at once
    vmulps xmm2, xmm0, xmm1

    ; return result in r8
    movaps [r8], xmm2
    ret

; scalar division
vec4_div_s:
    movaps xmm0, [rcx]
    movss xmm1, [rdx]
    shufps xmm1, xmm1, 0x00 ; shuffles term 0 into terms 0 1 2 and 3

    ; divide all terms at once
    vdivps xmm2, xmm0, xmm1

    ; return result in r8
    movaps [r8], xmm2
    ret

vec4_dot:
    ; move all terms into xmm registers
    load_xmm

    ; call vdpps on loaded terms (vector dot-product packed single-precision)
    vdpps xmm0, xmm0, xmm1, 0xFF ; return in xmm0
    ret

vec4_cross:
    ; move all terms into xmm registers
    load_xmm

    ; shuffle left side of subtraction
    movaps xmm2, xmm0
    shufps xmm2, xmm2, 0xC9

    movaps xmm3, xmm1
    shufps xmm3, xmm3, 0xD2

    vmulps xmm2, xmm2, xmm3

    ; shuffle right side of subtraction
    shufps xmm0, xmm0, 0xD2
    shufps xmm1, xmm1, 0xC9

    vmulps xmm0, xmm0, xmm1

    ; perform subtraction
    vsubps xmm2, xmm2, xmm0
    vandps xmm2, xmm2, [cross_mask]

    ; return result of cross product in r8
    movaps [r8], xmm2
    ret

vec4_length:
    ; load self twice
    movaps xmm0, [rcx]
    movaps xmm1, [rcx]

    ; result of dot product with self is length squared
    vdpps xmm0, xmm0, xmm1, 0xFF

    xorps xmm2, xmm2
    comiss xmm0, xmm2
    je .zero

    rsqrtss xmm1, xmm0

    ; perform one iteration of newton-raphson to improve accuracy
    movss xmm2, [const_0_5]
    vmulss xmm2, xmm2, xmm0
    vmulss xmm2, xmm2, xmm1
    vmulss xmm2, xmm2, xmm1

    movss xmm3, [const_1_5]
    vsubss xmm3, xmm3, xmm2
    vmulss xmm1, xmm1, xmm3

    ; convert inverse sqrt to normal sqrt
    vmulss xmm0, xmm0, xmm1 ; return in xmm0 
    ret

.zero:
    vxorps xmm0, xmm0, xmm0
    ret

vec4_normalize:
    sub rsp, 40
    call vec4_length
    add rsp, 40

    xorps xmm2, xmm2
    comiss xmm0, xmm2
    je .zero

    shufps xmm0, xmm0, 0x00
    movaps xmm1, [rcx]
    vdivps xmm1, xmm1, xmm0
    movaps [rdx], xmm1
    ret

.zero:
    vxorps xmm1, xmm1, xmm1
    movaps [rdx], xmm1
    ret

vec4_minimum:
    movaps xmm0, [rcx]
    movaps xmm1, [rdx]
    vminps xmm2, xmm0, xmm1
    movaps [r8], xmm2
    ret

vec4_maximum:
    movaps xmm0, [rcx]
    movaps xmm1, [rdx]
    vmaxps xmm2, xmm0, xmm1
    movaps [r8], xmm2
    ret

vec4_round:
    movaps xmm0, [rcx]
    roundps xmm0, xmm0, 0
    movaps [r8], xmm0
    ret

vec4_radians:
    movaps xmm0, [rcx]
    movss xmm1, [const_deg2rad]
    shufps xmm1, xmm1, 0x00

    vmulps xmm2, xmm0, xmm1
    movaps [r8], xmm2

    ret

vec4_degrees:
    movaps xmm0, [rcx]
    movss xmm1, [const_rad2deg]
    shufps xmm1, xmm1, 0x00

    vmulps xmm2, xmm0, xmm1
    movaps [r8], xmm2
    
    ret