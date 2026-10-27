default rel

section .data
    align 16
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
    vmovaps xmm0, [rcx]
    vmovaps xmm1, [rdx]
%endmacro

; 1st = rcx, 2nd = rdx
vec4_add:
    ; move all terms into xmm registers
    load_xmm

    ; add all terms at once
    vaddps xmm2, xmm0, xmm1
    
    vmovaps [r8], xmm2
    ret

vec4_sub:
    ; move all terms into xmm registers
    load_xmm

    ; subtract all terms at once
    vsubps xmm2, xmm0, xmm1

    vmovaps [r8], xmm2
    ret

; scalar multiplication
vec4_mul_s:
    vmovaps xmm0, [rcx]
    vmovss xmm1, [rdx]
    vshufps xmm1, xmm1, xmm1, 0x00 ; shuffles term 0 into terms 0 1 2 and 3

    ; multiply all terms at once
    vmulps xmm2, xmm0, xmm1

    ; return result in r8
    vmovaps [r8], xmm2
    ret

; scalar division
vec4_div_s:
    vmovaps xmm0, [rcx]
    vmovss xmm1, [rdx]
    vshufps xmm1, xmm1, xmm1, 0x00 ; shuffles term 0 into terms 0 1 2 and 3

    ; divide all terms at once
    vdivps xmm2, xmm0, xmm1

    ; return result in r8
    vmovaps [r8], xmm2
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
    vmovaps xmm2, xmm0
    vshufps xmm2, xmm2, xmm2, 0xC9

    vmovaps xmm3, xmm1
    vshufps xmm3, xmm3, xmm3, 0xD2

    vmulps xmm2, xmm2, xmm3

    ; shuffle right side of subtraction
    vshufps xmm0, xmm0, xmm0, 0xD2
    vshufps xmm1, xmm1, xmm1, 0xC9

    vmulps xmm0, xmm0, xmm1

    ; perform subtraction
    vsubps xmm2, xmm2, xmm0
    vandps xmm2, xmm2, [cross_mask]

    ; return result of cross product in r8
    vmovaps [r8], xmm2
    ret

vec4_length:
    ; load self twice
    vmovaps xmm0, [rcx]
    vmovaps xmm1, [rcx]

    ; result of dot product with self is length squared
    vdpps xmm0, xmm0, xmm1, 0xFF

    vxorps xmm2, xmm2, xmm2
    vcomiss xmm0, xmm2
    je .zero

    vrsqrtss xmm1, xmm1, xmm0

    ; perform one iteration of newton-raphson to improve accuracy
    vmovss xmm2, [const_0_5]
    vmulss xmm2, xmm2, xmm0
    vmulss xmm2, xmm2, xmm1
    vmulss xmm2, xmm2, xmm1

    vmovss xmm3, [const_1_5]
    vsubss xmm3, xmm3, xmm2
    vmulss xmm1, xmm1, xmm3

    ; convert inverse sqrt to normal sqrt
    vmulss xmm0, xmm0, xmm1 ; return in xmm0 
    ret

.zero:
    vxorps xmm0, xmm0, xmm0
    ret

vec4_normalize:
    ; align stack and call length of vec4 returned in xmm0
    sub rsp, 40
    call vec4_length
    add rsp, 40

    ; set xmm2 to 0 and compare with xmm0
    vxorps xmm2, xmm2, xmm2
    vcomiss xmm0, xmm2
    je .zero ; safety check for zero-length vectors

    ; broadcast scalar in xmm0 to all lanes
    vshufps xmm0, xmm0, xmm0, 0x00
    vmovaps xmm1, [rcx] ; load vector at mem in rcx into xmm1
    vdivps xmm1, xmm1, xmm0 ; divide xmm1 by xmm0 and store in xmm1
    vmovaps [rdx], xmm1 ; store at mem in rdx for return
    ret

.zero:
    vxorps xmm1, xmm1, xmm1 ; zero vector in xmm1 and return in mem at rdx
    vmovaps [rdx], xmm1
    ret

vec4_minimum:
    ; perform minimum on vectors at rcx and rdx and return result in r8
    vmovaps xmm0, [rcx]
    vmovaps xmm1, [rdx]
    vminps xmm2, xmm0, xmm1
    vmovaps [r8], xmm2
    ret

vec4_maximum:
    ; perform maximum on vectors at rcx and rdx and return result in r8
    vmovaps xmm0, [rcx]
    vmovaps xmm1, [rdx]
    vmaxps xmm2, xmm0, xmm1
    vmovaps [r8], xmm2
    ret

vec4_round:
    ; round vector at rcx to 0 decimal places and return in rdx
    vmovaps xmm0, [rcx]
    vroundps xmm0, xmm0, 0
    vmovaps [rdx], xmm0
    ret

vec4_radians:
    ; load vector at rcx to xmm0
    vmovaps xmm0, [rcx]
    ; move deg2rad const to xmm1 and broadcast to all lanes
    vmovss xmm1, [const_deg2rad]
    vshufps xmm1, xmm1, xmm1, 0x00

    ; perform multiplication between vector (xmm0) and deg2rad const (xmm1) and return in rdx
    vmulps xmm2, xmm0, xmm1
    vmovaps [rdx], xmm2

    ret

vec4_degrees:
    ; load vector at rcx to xmm0
    vmovaps xmm0, [rcx]
    ; move rad2deg const to xmm1 and broadcast to all lanes
    vmovss xmm1, [const_rad2deg]
    vshufps xmm1, xmm1, xmm1, 0x00

    ; perform multiplication between vector (xmm0) and rad2deg const (xmm1) and return in rdx
    vmulps xmm2, xmm0, xmm1
    vmovaps [rdx], xmm2
    
    ret