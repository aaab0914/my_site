# analyze_logs.py
import re
from collections import Counter


def analyze_logs(log_file):
    with open(log_file, 'r') as f:
        logs = f.readlines()

    # 提取用户 IP
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    ips = [ip_pattern.search(line).group(1) for line in logs if ip_pattern.search(line)]

    # 统计访问次数
    ip_counts = Counter(ips)
    top_ips = ip_counts.most_common(10)
    print("访问次数最多的 IP:")
    for ip, count in top_ips:
        print(f"  {ip}: {count} 次")