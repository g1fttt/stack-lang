ghoul proc begin
    1000 dup !i stdout

    true while begin
        i 7 - dup
        !i stdout
        i 0 >=
    end
end

ghoul
