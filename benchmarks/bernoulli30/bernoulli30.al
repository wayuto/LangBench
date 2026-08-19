import io

fun(pure) binomial(n: int, k: int): int {
    if k == 0 || k == n {
        return 1
    }
    binomial(n - 1, k - 1) + binomial(n - 1, k)
}

fun(pure) bernoulli(n: int): float {
    if n == 0 {
        return 1.0
    }
    if n == 1 {
        return -0.5
    }
    if n % 2 == 1 && n > 1 {
        return 0.0
    }
    
    var sum = 0.0
    for k in 0..n {
        sum += binomial(n, k)@float * bernoulli(k) / (n - k + 1)@float
    }
    return -sum
}

fun main(): int {
    var n = bernoulli(30)
    io::println(f"{n}")
    return 0
}