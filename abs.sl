proc cmp_clear
    swap drop swap drop
endproc

proc abs
    size 1 <
    cmp_clear call
    if back endif
    dup dup -
endproc

-1337
abs call
print
