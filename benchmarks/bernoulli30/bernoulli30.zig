const std = @import("std");

fn binomial(n: u32, k: u32) u64 {
    if (k == 0 or k == n) {
        return 1;
    }
    return binomial(n-1, k-1) + binomial(n-1, k);
}

fn bernoulli(n: u32) f64 {
    if (n == 0) {
        return 1.0;
    }
    if (n == 1) {
        return -0.5;
    }
    if (n % 2 == 1 and n > 1) {
        return 0.0;
    }
    
    var sum: f64 = 0.0;
    for (0..n) |k| {
        const k32: u32 = @intCast(k);
        sum += @as(f64, @floatFromInt(binomial(n, k32))) * bernoulli(k32) / @as(f64, @floatFromInt(n - k32 + 1));
    }
    return -sum;
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("{}\n", .{bernoulli(30)});
}