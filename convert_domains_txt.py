#!/usr/bin/env python3
"""
将纯文本域名列表转换为 SingBox 规则集 JSON 格式。
每行一个域名（忽略空行和注释行）。
"""

import json
import os
import sys


def convert_domain_txt_to_singbox(input_file: str, output_file: str) -> bool:
    """
    转换纯文本域名列表到 SingBox 规则集。

    域名列表中的每个条目都被视为 domain_suffix，
    与 Clash 的 DOMAIN-SUFFIX 行为一致。
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Error reading {input_file}: {e}")
        return False

    domain_suffix = []
    for line in lines:
        line = line.strip()
        # 跳过空行和注释
        if not line or line.startswith("#"):
            continue
        domain_suffix.append(line)

    if not domain_suffix:
        print(f"No domains found in {input_file}")
        return False

    # 去重并排序，保持输出确定性
    domain_suffix = sorted(set(domain_suffix))

    singbox_data = {
        "version": 2,
        "rules": [
            {
                "domain_suffix": domain_suffix
            }
        ]
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(singbox_data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Error writing {output_file}: {e}")
        return False

    print(f"Successfully converted {input_file} -> {output_file} "
          f"({len(domain_suffix)} domains)")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_domains_txt.py <input.txt> <output.json>")
        sys.exit(1)

    ok = convert_domain_txt_to_singbox(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
