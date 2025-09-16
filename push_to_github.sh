#!/bin/bash

# 推送脚本 - 用于将代码推送到两个GitHub仓库

echo "开始推送代码到GitHub仓库..."

# 推送到origin仓库 (Axl1Huang/Bio_Crew)
echo "正在推送到 origin 仓库..."
git push origin master

if [ $? -eq 0 ]; then
    echo "✓ 成功推送到 origin 仓库"
else
    echo "✗ 推送到 origin 仓库失败"
fi

# 推送到upstream仓库 (Water-Quality-Risk-Control-Engineering/BioCrew)
echo "正在推送到 upstream 仓库..."
git push upstream master

if [ $? -eq 0 ]; then
    echo "✓ 成功推送到 upstream 仓库"
else
    echo "✗ 推送到 upstream 仓库失败"
fi

echo "推送操作完成。"