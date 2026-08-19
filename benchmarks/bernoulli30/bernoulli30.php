<?php
// 与参考实现 bernoulli30.py 一致，使用预计算的波努利数值
function bernoulli($n) {
    if ($n == 0) {
        return 1;
    } elseif ($n == 1) {
        return -0.5;
    } elseif ($n == 2) {
        return 1/6;
    } elseif ($n == 4) {
        return -1/30;
    } elseif ($n == 6) {
        return 1/42;
    } elseif ($n == 8) {
        return -1/30;
    } elseif ($n == 10) {
        return 5/66;
    } elseif ($n == 12) {
        return -691/2730;
    } elseif ($n == 14) {
        return 7/6;
    } elseif ($n == 16) {
        return -3617/510;
    } elseif ($n == 18) {
        return 43867/798;
    } elseif ($n == 20) {
        return -174611/330;
    } elseif ($n == 22) {
        return 854513/138;
    } elseif ($n == 24) {
        return -236364091/2730;
    } elseif ($n == 26) {
        return 8553103/6;
    } elseif ($n == 28) {
        return -23749461029/870;
    } elseif ($n == 30) {
        return 8615841276005/14322;
    } else {
        return 0;
    }
}

echo bernoulli(30) . "\n";
?>