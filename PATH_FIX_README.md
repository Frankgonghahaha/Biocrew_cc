# 路径配置修复说明

## 问题描述
在菌剂评估阶段，系统无法找到代谢模型目录，导致ReactionAdditionTool等关键工具无法执行。

## 修复措施
1. 创建了目录结构：/home/axlhuang/BioCrew/tools/outputs/metabolic_models/
2. 将现有的代谢模型文件从/home/axlhuang/BioCrew/outputs/metabolic_models/复制到了新目录
3. 为推荐的微生物（Pseudomonas putida GCF_052695785_1和Rhodococcus jostii GCF_000213405_1）创建了占位符文件

## 后续建议
1. 需要生成Pseudomonas putida和Rhodococcus jostii的完整代谢模型文件
2. 建议统一项目中的路径引用方式，避免类似问题再次发生
3. 可以考虑使用相对路径或环境变量来管理资源目录路径
