# scripts/reporter.py
import json
import statistics
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans', 'Droid Sans Fallback']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def format_time(seconds, decimals=4):
    """根据时间大小自动选择合适的单位"""
    if seconds >= 1:
        return f"{seconds:.{decimals}f}s"
    elif seconds >= 0.001:
        return f"{seconds * 1000:.{decimals}f}ms"
    else:
        return f"{seconds * 1000000:.{decimals}f}μs"

def generate_report(results_dir):
    results = []
    failed_results = []
    # 递归查找所有 JSON 结果文件
    for result_file in Path(results_dir).rglob("*.json"):
        with open(result_file, 'r') as f:
            data = json.load(f)

            # 尝试从数据本身获取信息（runner.py 已经添加了 language 和 suite）
            if 'language' in data and 'suite' in data:
                data['test_case'] = data['suite']

                if data.get('success', False) and data.get('successful_runs', 0) > 0:
                    results.append(data)
                else:
                    failed_results.append(data)

    df = pd.DataFrame(results)
    failed_df = pd.DataFrame(failed_results)

    print(f"Found {len(results)} successful results, {len(failed_results)} failed results")

    # 如果没有成功结果，跳过图表生成
    if len(df) > 0:
        generate_boxplot_chart(df)

    # 生成Markdown表格
    generate_results_table(df, failed_df)

    return df

def _language_colors(languages):
    cmap = plt.cm.tab20
    return {lang: cmap(i % 20) for i, lang in enumerate(sorted(languages))}

def _sample_times(row):
    """获取每次运行的原始时间列表；旧数据没有 times 字段时用聚合统计近似"""
    times = row.get('times')
    if isinstance(times, list) and len(times) > 0:
        return [t for t in times if isinstance(t, (int, float))]
    mean = row.get('average_time', 0)
    if mean <= 0:
        return []
    std = row.get('std_dev_time', 0) or 0
    q1 = max(0.0, mean - 0.6745 * std)
    q3 = mean + 0.6745 * std
    return [row.get('min_time', mean), q1, mean, q3, row.get('max_time', mean)]

def generate_boxplot_chart(df):
    """每个测试用例一张横向箱线图：展示各语言多次运行时间的分布（对数刻度）"""
    if len(df) == 0 or 'test_case' not in df or 'language' not in df:
        return

    test_cases = sorted(df['test_case'].unique())
    colors = _language_colors(df['language'].unique())
    n_cases = len(test_cases)

    fig, axes = plt.subplots(1, n_cases, figsize=(7 * n_cases, 10), squeeze=False)
    axes = axes[0]

    for ax, test_case in zip(axes, test_cases):
        test_data = df[df['test_case'] == test_case]

        langs = []
        boxes = []
        for _, row in test_data.iterrows():
            times = _sample_times(row)
            if len(times) > 0:
                langs.append(row['language'])
                boxes.append(times)

        if not boxes:
            continue

        # 按中位数排序（最快的在顶部）
        order = sorted(range(len(boxes)), key=lambda i: statistics.median(boxes[i]))
        langs = [langs[i] for i in order]
        boxes = [boxes[i] for i in order]

        bp = ax.boxplot(boxes, orientation='horizontal', patch_artist=True, tick_labels=langs, widths=0.6,
                        medianprops=dict(color='black', linewidth=1.5),
                        flierprops=dict(marker='o', markersize=3, alpha=0.5))

        for patch, lang in zip(bp['boxes'], langs):
            patch.set_facecolor(colors[lang])
            patch.set_alpha(0.8)

        ax.set_xscale('log')
        ax.set_xlabel('执行时间（秒, 对数刻度）')
        ax.set_title(f'{test_case} 执行时间分布', fontsize=14)
        ax.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    Path('report').mkdir(exist_ok=True)
    plt.savefig('report/boxplot.svg', format='svg')
    plt.close()

def generate_results_table(df, failed_df):
    # 生成Markdown格式的结果表格
    Path('report').mkdir(exist_ok=True)

    with open('README.md', 'w') as f:
        f.write('# LangBench 测试报告\n\n')

        # 添加图表
        if len(df) > 0 and 'test_case' in df.columns:
            f.write('## 性能图表\n\n')
            f.write('### 执行时间箱线图\n\n')
            f.write('![执行时间箱线图](report/boxplot.svg)\n\n')

        # 按测试用例分组（仅成功的数据）
        if len(df) > 0 and 'test_case' in df.columns:
            # 确定时间单位（根据最小值）
            min_time = df['average_time'].min()
            unit = 's'
            decimals = 4
            if min_time < 1:
                unit = 'ms'
                decimals = 3
            if min_time < 0.001:
                unit = 'μs'
                decimals = 1

            for test_case in df['test_case'].unique():
                f.write(f'## {test_case}\n\n')
                test_data = df[df['test_case'] == test_case]

                # 排序：按平均时间升序
                test_data = test_data.sort_values('average_time')

                f.write(f'| 语言 | 平均时间({unit}) | 中位数({unit}) | 最小时间({unit}) | 最大时间({unit}) | 标准差({unit}) | 成功率 |\n')
                f.write('|------|------------------|-----------------|------------------|------------------|-----------------|--------|\n')

                for _, row in test_data.iterrows():
                    success_rate = (row['successful_runs'] / row['total_runs']) * 100
                    times = _sample_times(row)
                    median = statistics.median(times) if times else row['average_time']
                    # 根据单位转换时间值
                    if unit == 's':
                        avg_str = f"{row['average_time']:.{decimals}f}"
                        med_str = f"{median:.{decimals}f}"
                        min_str = f"{row['min_time']:.{decimals}f}"
                        max_str = f"{row['max_time']:.{decimals}f}"
                        std_str = f"{row['std_dev_time']:.{decimals}f}"
                    elif unit == 'ms':
                        avg_str = f"{row['average_time'] * 1000:.{decimals}f}"
                        med_str = f"{median * 1000:.{decimals}f}"
                        min_str = f"{row['min_time'] * 1000:.{decimals}f}"
                        max_str = f"{row['max_time'] * 1000:.{decimals}f}"
                        std_str = f"{row['std_dev_time'] * 1000:.{decimals}f}"
                    else:  # μs
                        avg_str = f"{row['average_time'] * 1000000:.{decimals}f}"
                        med_str = f"{median * 1000000:.{decimals}f}"
                        min_str = f"{row['min_time'] * 1000000:.{decimals}f}"
                        max_str = f"{row['max_time'] * 1000000:.{decimals}f}"
                        std_str = f"{row['std_dev_time'] * 1000000:.{decimals}f}"

                    f.write(f"| {row['language']} | {avg_str} | {med_str} | {min_str} | {max_str} | {std_str} | {success_rate:.1f}% |\n")

                f.write('\n')

            # 总结
            f.write('## 总结\n\n')
            for test_case in df['test_case'].unique():
                test_data = df[df['test_case'] == test_case]
                fastest = test_data.loc[test_data['average_time'].idxmin()]
                f.write(f"- **{test_case}**: 最快语言是 {fastest['language']} "
                       f"(平均 {format_time(fastest['average_time'])})\n")
            f.write('\n')

        # 失败测试报告
        if len(failed_df) > 0 and 'test_case' in failed_df.columns:
            failed_test_cases = set(failed_df['test_case'].unique())
            if len(failed_test_cases) > 0:
                f.write('## 失败测试详情\n\n')

                # 按测试用例分组失败结果
                df_test_cases = set(df['test_case'].unique()) if 'test_case' in df.columns else set()
                all_test_cases = df_test_cases | failed_test_cases

                for test_case in all_test_cases:
                    failed_test_data = failed_df[failed_df['test_case'] == test_case]

                    if len(failed_test_data) > 0:
                        f.write(f'### {test_case} - 失败\n\n')

                        for _, row in failed_test_data.iterrows():
                            language = row.get('language', 'unknown')
                            error = row.get('error', 'unknown error')
                            f.write(f"#### {language}\n")
                            f.write(f"**错误信息**: `{error}`\n\n")

                            failures = row.get('failures')
                            if isinstance(failures, list) and failures:
                                f.write("**失败详情**:\n")
                                f.write("```\n")
                                for i, failure in enumerate(failures[:3], 1):
                                    f.write(f"尝试 {i}: {failure.get('error', 'unknown')}\n")
                                f.write("```\n\n")

                            if row.get('total_runs', 0) > 0 and row.get('successful_runs', 0) == 0:
                                f.write(f"- 总运行次数: {row['total_runs']}\n")
                                f.write(f"- 成功次数: 0\n")
                                f.write(f"- 失败率: 100%\n\n")

                        f.write('---\n\n')
        else:
            f.write('## 失败测试\n\n')
            f.write('✅ 所有测试均通过！\n\n')

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate benchmark reports')
    parser.add_argument('--results-dir', default='.', help='Directory containing result JSON files')
    args = parser.parse_args()

    df = generate_report(args.results_dir)
    print(f"Report generated successfully. Processed {len(df)} results.")

if __name__ == '__main__':
    main()
