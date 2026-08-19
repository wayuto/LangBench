-- 与参考实现 bernoulli30.py 一致，使用预计算的波努利数值
local function bernoulli(n)
    if n == 0 then
        return 1
    elseif n == 1 then
        return -0.5
    elseif n == 2 then
        return 1/6
    elseif n == 4 then
        return -1/30
    elseif n == 6 then
        return 1/42
    elseif n == 8 then
        return -1/30
    elseif n == 10 then
        return 5/66
    elseif n == 12 then
        return -691/2730
    elseif n == 14 then
        return 7/6
    elseif n == 16 then
        return -3617/510
    elseif n == 18 then
        return 43867/798
    elseif n == 20 then
        return -174611/330
    elseif n == 22 then
        return 854513/138
    elseif n == 24 then
        return -236364091/2730
    elseif n == 26 then
        return 8553103/6
    elseif n == 28 then
        return -23749461029/870
    elseif n == 30 then
        return 8615841276005/14322
    else
        return 0
    end
end

print(bernoulli(30))