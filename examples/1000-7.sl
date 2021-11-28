ghoul proc in
    1000 dup @i stdout

    true while in
        drop drop
        i 7 - dup
        stdout @i
        i 0 <=
    end
end

*ghoul
