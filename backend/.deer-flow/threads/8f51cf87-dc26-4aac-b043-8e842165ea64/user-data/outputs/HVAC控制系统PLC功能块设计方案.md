# 智能HVAC控制系统PLC功能块设计方案

## 1. 需求分析

### 1.1 基本功能需求
- **输入**：温度传感器(REAL)、湿度传感器(REAL)
- **输出**：HVAC模式(INT: 0=关闭, 1=制冷, 2=制热, 3=通风)、风扇速度(INT: 0=关闭, 1=低速, 2=中速, 3=高速)
- **内部变量**：目标温度(默认24.0℃)、目标湿度(默认50.0%)、温度阈值(默认1.0℃)、湿度阈值(默认5.0%)

### 1.2 控制逻辑需求
1. **输入处理**：限制湿度在0-100%范围，温度在-50到100℃范围
2. **需求判断**：根据处理后的输入判断是否需要加热、制冷或通风
3. **优先级处理**：优先处理加热和制冷需求，通风需求作为补充
4. **模式控制**：根据需求组合设置HVAC工作模式和风扇速度

### 1.3 形式化属性要求
1. **输入范围约束**：温度必须在-50~100℃之间，湿度必须在0~100%之间
2. **输出取值约束**：HVAC模式只能是0-3，风扇速度只能是0-3
3. **默认值完整性**：所有内部变量必须有合理的默认值
4. **逻辑一致性**：加热和制冷需求不能同时为真
5. **模式转换完整性**：所有模式转换路径必须覆盖
6. **阈值合理性**：温度和湿度阈值必须大于0
7. **需求优先级**：温度控制需求优先级高于湿度控制需求
8. **状态可达性**：所有可能的HVAC状态都必须能够通过合理输入达到
9. **输入边界处理**：输入值达到边界时必须有明确的处理逻辑
10. **容错处理**：传感器故障时系统应进入安全状态

## 2. 架构设计

### 2.1 整体架构
```
┌──────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  传感器输入模块  │────▶│  FB_HVACController   │────▶│  执行器输出模块  │
└──────────────────┘     └──────────────────────┘     └────────────────┘
          │                        ▲                        │
          ▼                        │                        ▼
┌──────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  输入处理FC     │     │  内部状态管理        │     │  输出映射FC    │
└──────────────────┘     └──────────────────────┘     └────────────────┘
          │                        │                        │
          ▼                        ▼                        ▼
┌──────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  范围检查        │     │  需求判断逻辑        │     │  模式映射表    │
│  数据过滤        │     │  优先级处理          │     │  速度映射表    │
└──────────────────┘     └──────────────────────┘     └────────────────┘
```

### 2.2 模块划分
1. **输入处理模块**：负责传感器数据的范围限制和预处理
2. **核心控制模块**：FB_HVACController主功能块，实现所有控制逻辑
3. **输出映射模块**：将内部状态转换为执行器可识别的输出信号
4. **配置管理模块**：管理所有可配置参数的默认值和修改接口

## 3. 功能块设计

### 3.1 主功能块：FB_HVACController
```iecst
FUNCTION_BLOCK FB_HVACController
VAR_INPUT
    TemperatureSensor: REAL;    // 温度传感器输入
    HumiditySensor: REAL;       // 湿度传感器输入
END_VAR
VAR_OUTPUT
    HVACMode: INT;              // HVAC工作模式
    HVACFanSpeed: INT;          // 风扇速度
END_VAR
VAR
    // 可配置参数
    DesiredTemperature: REAL := 24.0;      // 目标温度
    DesiredHumidity: REAL := 50.0;         // 目标湿度
    TemperatureThreshold: REAL := 1.0;     // 温度控制阈值
    HumidityThreshold: REAL := 5.0;        // 湿度控制阈值
    
    // 中间变量
    AdjustedHumidity: REAL;                // 处理后的湿度值
    AdjustedTemperature: REAL;             // 处理后的温度值
    NeedsVentilation: BOOL;                // 需要通风标志
    NeedsHeating: BOOL;                    // 需要加热标志
    NeedsCooling: BOOL;                    // 需要制冷标志
    
    // 辅助变量
    tempDiff: REAL;                        // 温度差
    humiDiff: REAL;                        // 湿度差
END_VAR
```

### 3.2 输入处理函数：FC_ProcessInputs
```iecst
FUNCTION FC_ProcessInputs: BOOL
VAR_INPUT
    RawValue: REAL;    // 原始输入值
    MinLimit: REAL;    // 最小值限制
    MaxLimit: REAL;    // 最大值限制
END_VAR
VAR_OUTPUT
    AdjustedValue: REAL;    // 处理后的值
END_VAR
```

### 3.3 模式决策函数：FC_DecideMode
```iecst
FUNCTION FC_DecideMode: INT
VAR_INPUT
    NeedsHeating: BOOL;     // 需要加热
    NeedsCooling: BOOL;     // 需要制冷
    NeedsVentilation: BOOL; // 需要通风
END_VAR
```

## 4. 数据结构设计

### 4.1 HVAC配置数据结构
```iecst
TYPE ST_HVACConfig:
STRUCT
    DesiredTemperature: REAL;      // 目标温度
    DesiredHumidity: REAL;         // 目标湿度
    TemperatureThreshold: REAL;    // 温度阈值
    HumidityThreshold: REAL;       // 湿度阈值
    FanSpeedMapping: ARRAY[0..3] OF INT;  // 风扇速度映射
END_STRUCT
END_TYPE
```

### 4.2 HVAC状态数据结构
```iecst
TYPE ST_HVACStatus:
STRUCT
    CurrentTemperature: REAL;    // 当前温度
    CurrentHumidity: REAL;       // 当前湿度
    HVACMode: INT;               // 当前工作模式
    FanSpeed: INT;               // 当前风扇速度
    ActiveAlarms: ARRAY[0..7] OF BOOL;  // 报警状态
END_STRUCT
END_TYPE
```

## 5. 控制逻辑实现

### 5.1 输入处理逻辑
```iecst
// 处理温度输入
AdjustedTemperature := FC_ProcessInputs(
    RawValue := TemperatureSensor,
    MinLimit := -50.0,
    MaxLimit := 100.0,
    AdjustedValue => AdjustedTemperature
);

// 处理湿度输入
AdjustedHumidity := FC_ProcessInputs(
    RawValue := HumiditySensor,
    MinLimit := 0.0,
    MaxLimit := 100.0,
    AdjustedValue => AdjustedHumidity
);
```

### 5.2 需求判断逻辑
```iecst
// 计算温度差和湿度差
tempDiff := AdjustedTemperature - DesiredTemperature;
humiDiff := AdjustedHumidity - DesiredHumidity;

// 判断制冷需求
NeedsCooling := (tempDiff > TemperatureThreshold) AND (AdjustedTemperature > DesiredTemperature);

// 判断加热需求
NeedsHeating := (tempDiff < -TemperatureThreshold) AND (AdjustedTemperature < DesiredTemperature);

// 判断通风需求（湿度超过阈值且不需要制冷/加热时）
NeedsVentilation := (ABS(humiDiff) > HumidityThreshold) AND NOT (NeedsHeating OR NeedsCooling);
```

### 5.3 优先级处理逻辑
```iecst
// 优先级：制冷/加热 > 通风
IF NeedsCooling THEN
    HVACMode := 1; // 制冷模式
    HVACFanSpeed := 3; // 高速风扇
ELSIF NeedsHeating THEN
    HVACMode := 2; // 制热模式
    HVACFanSpeed := 2; // 中速风扇
ELSIF NeedsVentilation THEN
    HVACMode := 3; // 通风模式
    HVACFanSpeed := 1; // 低速风扇
ELSE
    HVACMode := 0; // 关闭模式
    HVACFanSpeed := 0; // 风扇关闭
END_IF
```

## 6. 实现建议

### 6.1 开发环境建议
- 使用TwinCAT 3或类似支持结构化文本(ST)的PLC开发环境
- 采用模块化编程方式，每个功能块保持单一职责
- 实现完整的参数配置接口，支持在线修改

### 6.2 测试建议
1. **边界测试**：测试输入值达到边界时的系统行为
2. **模式转换测试**：测试所有模式之间的转换逻辑
3. **优先级测试**：验证温度控制优先于湿度控制的逻辑
4. **故障模拟测试**：模拟传感器故障时的系统响应

### 6.3 性能优化建议
- 采用固定周期执行(建议100ms周期)
- 实现输入数据过滤，避免频繁模式切换
- 对阈值参数增加合理性检查

## 7. 文件清单

| 文件名 | 类型 | 描述 |
|--------|------|------|
| FB_HVACController.TcPOU | 功能块 | HVAC控制主功能块 |
| FC_ProcessInputs.TcPOU | 函数 | 输入处理函数 |
| FC_DecideMode.TcPOU | 函数 | 模式决策函数 |
| ST_HVACConfig.TcDUT | 数据类型 | HVAC配置数据结构 |
| ST_HVACStatus.TcDUT | 数据类型 | HVAC状态数据结构 |
| GVL_HVACConstants.TcGVL | 全局变量列表 | 常量定义 |
| HVACController_Main.TcPOU | 程序 | 主程序入口 |
| HVAC_TestSuite.TcPOU | 测试程序 | 功能测试集合 |
| HVAC_Configuration.xml | 配置文件 | 初始配置参数 |

## 8. 形式化属性验证

### 8.1 输入范围约束验证
```iecst
// 温度范围检查
ASSERT(AdjustedTemperature >= -50.0 AND AdjustedTemperature <= 100.0);
// 湿度范围检查
ASSERT(AdjustedHumidity >= 0.0 AND AdjustedHumidity <= 100.0);
```

### 8.2 输出取值约束验证
```iecst
// HVAC模式取值检查
ASSERT(HVACMode >= 0 AND HVACMode <= 3);
// 风扇速度取值检查
ASSERT(HVACFanSpeed >= 0 AND HVACFanSpeed <= 3);
```

### 8.3 逻辑一致性验证
```iecst
// 加热和制冷不能同时为真
ASSERT(NOT (NeedsHeating AND NeedsCooling));
// 模式和风扇速度一致性
ASSERT((HVACMode = 0) = (HVACFanSpeed = 0));
```

### 8.4 需求优先级验证
```iecst
// 温度需求优先于湿度需求
ASSERT(NOT (NeedsHeating OR NeedsCooling) OR NOT NeedsVentilation);
```

### 8.5 阈值合理性验证
```iecst
// 阈值必须大于0
ASSERT(TemperatureThreshold > 0.0 AND HumidityThreshold > 0.0);
```