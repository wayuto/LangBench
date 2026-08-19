import io

fun(pure) fib(n: int): int {
    if n <= 1 {
        return n;
    }
    fib(n - 1) + fib(n - 2)
}

fun main(): int {
    var n = fib(42);
    io::println(f"{n}")
    return 0
}
