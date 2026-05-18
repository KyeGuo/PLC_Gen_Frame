#!/bin/bash

# 创建输出目录结构
mkdir -p /mnt/user-data/outputs/sources/DUT
mkdir -p /mnt/user-data/outputs/sources/FB
mkdir -p /mnt/user-data/outputs/sources/PRG
mkdir -p /mnt/user-data/outputs/reports

# 复制DUT文件
cp /mnt/user-data/workspace/E_MotorState.TcDUT /mnt/user-data/outputs/sources/DUT/
cp /mnt/user-data/workspace/E_ErrorCode.TcDUT /mnt/user-data/outputs/sources/DUT/
cp /mnt/user-data/workspace/DUT_MotorData.TcDUT /mnt/user-data/outputs/sources/DUT/

# 复制FB文件
cp /mnt/user-data/workspace/FB_MotorControl.TcPOU /mnt/user-data/outputs/sources/FB/
cp /mnt/user-data/workspace/FB_OverloadProtection.TcPOU /mnt/user-data/outputs/sources/FB/

# 复制PRG文件
cp /mnt/user-data/workspace/PRG_Main.TcPOU /mnt/user-data/outputs/sources/PRG/

# 复制报告文件
cp /mnt/user-data/workspace/validation_report.json /mnt/user-data/outputs/reports/

echo "文件已成功复制到输出目录"