# Museum Climate Control System - PLC Implementation Guide

## 1. 需求分析

### 功能需求
- **湿度控制**: 维持50%的目标湿度，低于50%启动加湿器，高于50%启动除湿器
- **温度控制**: 维持20°C的目标温度，偏离时启动HVAC系统
- **灯光控制**: 根据环境光传感器和阈值控制灯光开关
- **安全互锁**: 确保加湿器和除湿器不会同时运行

### 技术需求
- 符合TwinCAT 3 / IEC 61131-3标准
- 模块化设计，便于维护和扩展
- 内置安全机制，保护设备和藏品
- 清晰的接口定义，便于与其他系统集成

## 2. 架构设计

### 整体架构
```
┌─────────────────────────┐
│ 博物馆环境控制系统       │
├─────────────────────────┤
│ ▶ FB_MuseumClimateControl │
│   ├─ ControlHumidity     │
│   ├─ ControlTemperature   │
│   ├─ ControlLighting      │
│   └─ SafetyInterlock      │
├─────────────────────────┤
│ 输入: 传感器信号          │
│ 输出: 执行器控制信号      │
└─────────────────────────┘
```

### 模块划分
- **湿度控制模块**: 处理湿度传感器输入，控制加湿器和除湿器
- **温度控制模块**: 处理温度传感器输入，控制HVAC系统
- **灯光控制模块**: 处理光线传感器和阈值输入，控制灯光
- **安全互锁模块**: 提供设备互锁保护，防止冲突操作

## 3. 功能块设计

### FB_MuseumClimateControl

#### 功能描述
核心功能块，整合所有控制逻辑，提供统一的传感器输入和执行器输出接口。

#### 输入参数
| 参数名称 | 类型 | 描述 |
|---------|------|------|
| HumiditySensor | REAL | 湿度传感器读数 (%) |
| TemperatureSensor | REAL | 温度传感器读数 (°C) |
| LightSensor | BOOL | 光线传感器状态 (TRUE=检测到光线) |
| LightThreshold | BOOL | 灯光控制阈值 (TRUE=启用自动控制) |

#### 输出参数
| 参数名称 | 类型 | 描述 |
|---------|------|------|
| HVACSystem | BOOL | HVAC系统控制输出 (TRUE=开启) |
| Humidifier | BOOL | 加湿器控制输出 (TRUE=开启) |
| Dehumidifier | BOOL | 除湿器控制输出 (TRUE=开启) |
| LightControl | BOOL | 灯光控制输出 (TRUE=开启) |

#### 内部变量
| 变量名称 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| HumiditySetpoint | REAL | 50.0 | 目标湿度设置值 (%) |
| TemperatureSetpoint | REAL | 20.0 | 目标温度设置值 (°C) |

#### 方法定义
- `ControlHumidity()`: 湿度控制逻辑实现
- `ControlTemperature()`: 温度控制逻辑实现
- `ControlLighting()`: 灯光控制逻辑实现
- `SafetyInterlock()`: 安全互锁逻辑实现

## 4. 数据结构设计

### 传感器数据结构
```st
TYPE ST_SensorData :
STRUCT
    Humidity : REAL;
    Temperature : REAL;
    LightDetected : BOOL;
END_STRUCT
END_TYPE
```

### 执行器控制结构
```st
TYPE ST_ActuatorControl :
STRUCT
    HVAC : BOOL;
    Humidifier : BOOL;
    Dehumidifier : BOOL;
    Lights : BOOL;
END_STRUCT
END_TYPE
```

### 系统状态结构
```st
TYPE ST_SystemStatus :
STRUCT
    SensorData : ST_SensorData;
    ActuatorControl : ST_ActuatorControl;
    SystemOK : BOOL;
    ErrorCode : WORD;
END_STRUCT
END_TYPE
```

## 5. 实现建议

### 编程建议
1. **使用结构化文本(ST)** 实现功能块，提高可读性和维护性
2. **模块化设计** 将不同控制逻辑分离到独立方法中
3. **添加注释** 详细说明控制逻辑和参数含义
4. **错误处理** 考虑添加传感器故障检测和报警功能

### 调试建议
1. **监控变量** 在TwinCAT中监控关键变量，验证控制逻辑
2. **模拟测试** 使用TwinCAT的模拟功能测试各种场景
3. **逐步调试** 分模块测试控制逻辑，确保每个模块正常工作
4. **边界测试** 测试湿度50%和温度20°C的边界情况

### 优化建议
1. **添加死区** 为湿度和温度控制添加死区，避免频繁启停
2. **参数化** 将设置值改为可配置参数，提高灵活性
3. **历史记录** 添加数据记录功能，存储温湿度历史数据
4. **远程监控** 实现数据上传和远程控制功能

## 6. 文件清单

| 文件名称 | 类型 | 描述 |
|---------|------|------|
| FB_MuseumClimateControl.TcPOU | PLC功能块 | 核心控制逻辑实现 |
| FB_MuseumClimateControl_Interface.md | 文档 | 功能块接口说明 |
| MuseumClimateControl_ImplementationGuide.md | 文档 | 完整实现指南 |
| ST_SensorData.TcDUT | 数据类型 | 传感器数据结构 |
| ST_ActuatorControl.TcDUT | 数据类型 | 执行器控制结构 |
| ST_SystemStatus.TcDUT | 数据类型 | 系统状态结构 |
| GVL_MuseumClimate.TcGVL | 全局变量列表 | 全局参数和配置 |

## 7. 安全考虑

### 设备保护
- 加湿器和除湿器互锁，防止同时运行
- HVAC系统有过热保护
- 所有输出有短路保护

### 藏品保护
- 精确的温湿度控制，保护文物不受损害
- 灯光控制避免文物褪色
- 系统故障时自动切换到安全模式

## 8. 维护建议

### 定期维护
1. 校准传感器 (每6个月)
2. 清洁加湿器和除湿器滤网 (每3个月)
3. 检查HVAC系统运行状态 (每年)
4. 测试安全互锁功能 (每季度)

### 故障排除
| 故障现象 | 可能原因 | 解决方法 |
|---------|---------|---------|
| 加湿器和除湿器同时运行 | 逻辑错误 | 检查安全互锁功能 |
| HVAC系统频繁启停 | 传感器波动 | 添加死区或滤波 |
| 灯光不响应 | 传感器故障 | 检查光线传感器 |
| 系统无输出 | 电源故障 | 检查供电和接线 |