#!/bin/bash

# 设置基础目录
base_dir="output"

# 遍历输出目录下的所有子目录
find "$base_dir" -type f -name "*.json" | while read -r json_file; do
    # 获取目录路径
    dir_path=$(dirname "$json_file")
    
    # 获取文件名（不含扩展名）
    filename=$(basename "$json_file" .json)
    
    # 构建输出文件路径
    output_file="$dir_path/$filename.srs"
    
    # 执行编译命令
    echo "Compiling $json_file to $output_file"
    sing-box rule-set compile --output "$output_file" "$json_file"
done

echo "All rule sets compiled successfully!"
