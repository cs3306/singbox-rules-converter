#!/usr/bin/env python3
import yaml
import json
import sys
import os
import glob

def get_rule_type_value(rule_type):
    """将Clash规则类型转换为SingBox规则类型"""
    mapping = {
        "DOMAIN-SUFFIX": "domain_suffix",
        "DOMAIN-KEYWORD": "domain_keyword",
        "DOMAIN": "domain",
        "IP-CIDR": "ip_cidr",
        "IP-CIDR6": "ip_cidr"
    }
    return mapping.get(rule_type, "")

def convert_clash_yaml_to_singbox(input_file, output_file, outbound):
    """转换YAML格式的Clash规则到SingBox规则集"""
    # 创建SingBox规则集基础结构
    singbox_data = {
        "version": 3,
        "rules": []
    }
    
    # 读取并解析YAML文件
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            try:
                clash_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {input_file}: {e}")
                return False
        
        # 提取规则
        rules = clash_data.get("payload", [])
        if not rules:
            print(f"No rules found in {input_file}")
            return False
        
        # 按规则类型分组收集规则
        rule_groups = {}
        
        for rule in rules:
            parts = rule.split(",")
            if len(parts) < 2:
                continue
            
            rule_type = parts[0]
            value = parts[1]
            
            # 获取SingBox规则类型
            singbox_rule_type = get_rule_type_value(rule_type)
            if not singbox_rule_type:
                # 不支持的规则类型
                continue
                
            # 将规则添加到对应类型组中
            if singbox_rule_type not in rule_groups:
                rule_groups[singbox_rule_type] = []
            rule_groups[singbox_rule_type].append(value)
        
        # 为每个规则类型创建一个规则项
        for rule_type, values in rule_groups.items():
            singbox_rule = {
                "type": rule_type,
                "payload": values
            }
            singbox_data["rules"].append(singbox_rule)
        
        # 保存为JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(singbox_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error processing file {input_file}: {e}")
        return False

def convert_dir(input_dir, output_dir, source_name):
    """处理整个目录的规则文件"""
    success_count = 0
    fail_count = 0
    
    # 查找所有YAML规则文件
    yaml_files = []
    for ext in ["*.yaml", "*.yml"]:
        yaml_files.extend(glob.glob(os.path.join(input_dir, "**", ext), recursive=True))
    
    print(f"Found {len(yaml_files)} YAML files in {input_dir}")
    
    for yaml_file in yaml_files:
        # 判断这个文件是否是规则文件
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if not isinstance(content, dict) or "payload" not in content:
                    # 不是规则文件，跳过
                    continue
        except:
            # 无法解析，跳过
            continue
        
        # 构建输出文件路径
        rel_path = os.path.relpath(yaml_file, input_dir)
        category = os.path.dirname(rel_path).replace("\\", "/")
        filename = os.path.basename(yaml_file).split(".")[0]
        
        output_json = os.path.join(output_dir, source_name, category, f"{filename}.json")
        
        # 确定出站策略 (仅用于日志，不再写入规则)
        outbound = get_outbound(category, filename)
        
        # 转换文件
        if convert_clash_yaml_to_singbox(yaml_file, output_json, outbound):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"Conversion complete: {success_count} succeeded, {fail_count} failed")
    return success_count

def get_outbound(category, filename):
    """根据规则类别和文件名决定出站策略"""
    filename = filename.lower()
    
    # 广告拦截规则
    if any(keyword in filename for keyword in ["ad", "ads", "advert", "advertising", "ban", "reject", "privacy"]):
        return "block"
    
    # 直连规则
    if any(keyword in filename for keyword in ["china", "cn", "direct", "mainland", "domestic"]):
        return "direct"
    
    # 默认为代理
    return "proxy"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python convert_rules.py <input_dir> <output_dir> <source_name>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    source_name = sys.argv[3]
    
    count = convert_dir(input_dir, output_dir, source_name)
    print(f"Successfully converted {count} rule files from {source_name}")
