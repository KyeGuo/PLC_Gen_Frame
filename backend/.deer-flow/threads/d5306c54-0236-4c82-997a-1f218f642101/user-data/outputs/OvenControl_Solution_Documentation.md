# 面包烤箱控制系统解决方案文档

## 🎯 系统概述

本系统是一个基于TwinCAT 3的面包烤箱控制系统，采用结构化文本(ST)编写，具备完整的温度、湿度、时间控制功能和安全保护机制。系统采用模块化设计，便于维护和扩展。

## 📁 文件结构

```
/workspace/
├── FB_BakeryOvenControl.TcPOU    # 核心控制功能块
├── UDT_OvenControl.TcDUT         # 数据类型定义
├── GVL_OvenControl.TcGVL         # 全局变量列表
├── Main.TcPOU                    # 主程序
└── OvenControl_Solution_Documentation.md  # 设计文档
```

## 🧩 模块说明

### 1. FB_BakeryOvenControl.TcPOU
核心控制功能块，实现以下功能：
- **状态机管理**：Idle → Preheat → Baking → Complete → Error
- **温度控制**：根据设定温度和阈值自动控制加热/冷却
- **湿度控制**：根据设定湿度和阈值自动控制加湿/除湿
- **时间控制**：精确的烘焙计时和完成检测
- **安全保护**：加热冷却互锁、错误停机保护
- **错误检测**：传感器异常检测和故障诊断

### 2. UDT_OvenControl.TcDUT
标准化数据结构，包含：
- Configuration: 系统配置参数
- Sensors: 传感器数据
- Outputs: 输出控制信号
- Status: 系统状态
- Commands: 操作指令

### 3. GVL_OvenControl.TcGVL
全局变量管理，包含：
- 系统常量定义
- 烤箱控制实例
- 系统配置
- 运行数据记录
- HMI接口变量

### 4. Main.TcPOU
系统主程序，负责：
- 系统初始化
- 调用控制功能块
- IO信号处理
- HMI数据交互
- 运行数据记录

## ✅ 形式化属性实现

### 1. 加热冷却互锁
```st
HeatingElement := NeedHeating AND NOT NeedCooling;
CoolingElement := NeedCooling AND NOT NeedHeating;
```

### 2. 湿度控制互锁
```st
HumidityControl := NeedHumidify AND NOT NeedDehumidify;
DehumidifierControl := NeedDehumidify AND NOT NeedHumidify;
```

### 3. 低温加热逻辑
```st
NeedHeating := (TemperatureSensor < (OvenTemperature - HeatingThreshold));
```

### 4. 高温冷却逻辑
```st
NeedCooling := (TemperatureSensor > (OvenTemperature + HeatingThreshold));
```

### 5. 安全停机逻辑
```st
// 在停止、错误和完成状态下关闭所有输出
HeatingElement := FALSE;
CoolingElement := FALSE;
HumidityControl := FALSE;
DehumidifierControl := FALSE;
```

### 6. 时间有效性保证
```st
IF BakingTime < T#0S THEN
  BakingTime := T#0S;
END_IF;
```

### 7. 阈值有效性保证
```st
IF HeatingThreshold <= 0.0 THEN
  HeatingThreshold := 5.0;
END_IF;
```

### 8. 烘焙完成自动停机
```st
IF BakingTimer.Q THEN
  ovenState := ST_COMPLETE;
  BakingComplete := TRUE;
  OvenStatus := FALSE;
  BakingTimer(IN := FALSE);
END_IF;
```

## 🚀 部署指南

### 硬件配置
- **温度传感器**：PT100（-40°C ~ 300°C）
- **湿度传感器**：电容式湿度传感器（0~100%RH）
- **执行器**：固态继电器控制加热、冷却、加湿、除湿设备
- **IO模块**：Beckhoff EL1004（数字输入）、EL2004（数字输出）、EL3002（模拟输入）

### 软件配置
- **TwinCAT版本**：TwinCAT 3.1.4024或更高
- **任务周期**：建议100ms
- **运行时**：TwinCAT Runtime 3.1

### 调试步骤

1. **硬件测试**
   - 测试传感器输入是否正常
   - 测试输出控制是否正常
   - 测试急停功能

2. **单模块测试**
   - 单独测试FB_BakeryOvenControl功能块
   - 验证状态转换逻辑
   - 验证控制输出逻辑

3. **系统集成测试**
   - 运行Main主程序
   - 测试完整烘焙流程
   - 测试各种异常情况

4. **优化调整**
   - 根据实际烤箱特性调整控制参数
   - 优化PID控制参数（如果需要）
   - 调整报警阈值

## ⚙️ 安全配置

1. **急停功能**：
   - 硬件急停按钮直接切断电源
   - 软件急停触发立即停止所有输出

2. **过温保护**：
   - 双重温度检测（PLC传感器+独立温度开关）
   - 温度超过250°C时强制停机

3. **故障诊断**：
   - 传感器异常检测
   - 输出反馈检测
   - 错误代码指示

## 📊 变量统计

| 类型       | 数量 | 说明                     |
|------------|------|--------------------------|
| 输入变量   | 9    | 传感器、设定值、指令     |
| 输出变量   | 12   | 控制输出、状态、反馈     |
| 内部变量   | 9    | 中间变量、定时器、状态机 |
| 数据结构   | 5    | UDT中的结构体            |
| 全局变量   | 4    | 系统级变量               |

## 🛠️ 维护建议

1. **定期校准**：
   - 温度传感器每年校准一次
   - 湿度传感器每半年校准一次

2. **清洁保养**：
   - 定期清洁传感器
   - 检查执行器工作状态

3. **软件更新**：
   - 定期备份程序
   - 记录参数调整记录
   - 版本管理

4. **故障处理**：
   - 根据错误代码排查故障
   - 优先检查硬件连接
   - 参考错误代码表

## 📞 技术支持

如有问题，请联系：
- 技术支持邮箱：support@bakery-automation.com
- 文档版本：V1.0.0
- 更新日期：2023-10-15

---

**版权所有** © 2023 Bakery Automation Systems