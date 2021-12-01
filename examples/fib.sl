fib proc begin
    size 1 >= if begin
        !n 1 1 !a !b

        0 !i
        true while begin
            a b + !s
            b !a
            s !b
            i 1 + !i
            n 2 - i swap <
        end

        b
    end
end

100 fib stdout
