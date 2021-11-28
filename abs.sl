cmp_clear proc in
    swap drop swap drop
end

abs proc in
    size 1 >=
    *cmp_clear
    if in
        dup dup -
    end
end

-1337 *abs stdout
