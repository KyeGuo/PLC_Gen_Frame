# 精密金属雕刻机控制系统PLC功能块设计方案

## 1. 需求分析

### 功能需求
- 根据设计选择参数自动配置雕刻工艺参数
- 支持3种预设设计模式，每种模式对应不同的雕刻速度和深度
- 无效设计选择时自动禁用所有电机并重置参数
- 设计更改时操作可重复，确保状态一致性

### 输入输出定义
| 类型       | 名称              | 数据类型 | 描述                                 |
|------------|-------------------|----------|--------------------------------------|
| **输入变量** | DesignSelection   | INT      | 设计选择: 1=设计1, 2=设计2, 3=设计3   |
| **输入变量** | EngravingDepth    | REAL     | 外部输入雕刻深度（备用参数）          |
| **输入变量** | EngravingSpeed    | REAL     | 外部输入雕刻速度（备用参数）          |
| **输出变量** | ZAxisMotor        | BOOL     | Z轴电机使能输出（TRUE=激活）          |
| **输出变量** | EngravingMotor    | BOOL     | 雕刻电机使能输出（TRUE=激活）        |
| **内部变量** | CalculatedDepth   | REAL     | 内部计算的实际雕刻深度               |
| **内部变量** | CalculatedSpeed   | REAL     | 内部计算的实际雕刻速度               |

### 设计模式参数
| 设计编号 | 雕刻速度 | 雕刻深度 |
|----------|----------|----------|
| 1        | 10.0     | 0.1      |
| 2        | 8.0      | 0.2      |
| 3        | 12.0     | 0.15     |
| 其他     | 0.0      | 0.0      |

## 2. 架构设计

### 整体架构图
```
┌─────────────────────────────────────────────────┐
│          FB_EngravingController                 │
│  ┌───────────┐     ┌─────────────────────────┐  │
│  │ 输入处理  │────▶│ 参数设置方法SetParamsByDesign │  │
│  └───────────┘     └─────────────────────────┘  │
│                │                                │
│                ▼                                │
│  ┌─────────────────────────┐     ┌───────────┐  │
│  │ 电机状态更新方法UpdateMotorStates │────▶│ 输出处理  │  │
│  └─────────────────────────┘     └───────────┘  │
│                │                                │
│                ▼                                │
│  ┌─────────────────────────┐                    │
│  │ 状态保持（PreviousDesign） │                    │
│  └─────────────────────────┘                    │
└─────────────────────────────────────────────────┘
```

### 模块划分
1. **输入处理模块**: 检测设计选择变更
2. **参数设置模块**: 根据设计选择配置工艺参数
3. **电机控制模块**: 根据设计有效性控制电机状态
4. **状态保持模块**: 记录上一次设计选择，确保操作可重复

## 3. 功能块设计

### FB_EngravingController 功能块
```st
FUNCTION_BLOCK FB_EngravingController
VAR_INPUT
    DesignSelection : INT; // 设计选择输入
    EngravingDepth : REAL; // 外部深度输入
    EngravingSpeed : REAL; // 外部速度输入
END_VAR
VAR_OUTPUT
    ZAxisMotor : BOOL; // Z轴电机输出
    EngravingMotor : BOOL; // 雕刻电机输出
END_VAR
VAR
    CalculatedDepth : REAL; // 内部计算深度
    CalculatedSpeed : REAL; // 内部计算速度
    PreviousDesign : INT; // 上一次设计选择
END_VAR
```

### 方法定义

#### SetParametersByDesign 方法
```st
METHOD SetParametersByDesign
VAR_INPUT
    Design : INT;
END_VAR
CASE Design OF
    1: // 设计1参数配置
        CalculatedSpeed := 10.0;
        CalculatedDepth := 0.1;
    2: // 设计2参数配置
        CalculatedSpeed := 8.0;
        CalculatedDepth := 0.2;
    3: // 设计3参数配置
        CalculatedSpeed := 12.0;
        CalculatedDepth := 0.15;
    ELSE: // 无效设计处理
        CalculatedSpeed := 0.0;
        CalculatedDepth := 0.0;
END_CASE;
END_METHOD
```

#### UpdateMotorStates 方法
```st
METHOD UpdateMotorStates
VAR_INPUT
    IsValidDesign : BOOL;
END_VAR
IF IsValidDesign THEN
    ZAxisMotor := TRUE;
    EngravingMotor := TRUE;
ELSE
    ZAxisMotor := FALSE;
    EngravingMotor := FALSE;
END_IF;
END_METHOD
```

### 主逻辑流程
```st
// 检测设计选择变化
IF DesignSelection <> PreviousDesign THEN
    // 更新工艺参数
    SetParametersByDesign(Design := DesignSelection);
    // 记录当前设计选择
    PreviousDesign := DesignSelection;
END_IF;

// 更新电机状态
UpdateMotorStates(IsValidDesign := (DesignSelection >= 1 AND DesignSelection <= 3));
```

## 4. 数据结构设计

### 参数配置结构体（可选扩展）
```st
TYPE ST_DesignParameters :
STRUCT
    Speed : REAL;
    Depth : REAL;
END_STRUCT
END_TYPE
```

### 配置数组（可选扩展）
```st
VAR_GLOBAL CONSTANT
    DesignConfigurations : ARRAY[1..3] OF ST_DesignParameters := [
        (Speed := 10.0, Depth := 0.1),  // 设计1
        (Speed := 8.0, Depth := 0.2),   // 设计2
        (Speed := 12.0, Depth := 0.15)  // 设计3
    ];
END_VAR
```

## 5. 实现建议

### 编程注意事项
1. **原子性操作**: 设计切换时确保参数更新和电机状态变更的原子性
2. **状态保持**: 使用PreviousDesign变量确保设计更改操作可重复执行
3. **边界处理**: 严格处理无效设计输入（非1-3的所有值）
4. **实时性**: 主逻辑应在每个扫描周期执行，确保响应及时性

### 故障安全设计
- 初始状态下所有电机禁用
- 无效设计选择时自动禁用电机并重置参数
- 电源恢复后保持安全状态

### 扩展性建议
1. 可添加参数范围检查功能
2. 可实现外部输入参数与预设参数的切换逻辑
3. 可添加参数修改记录和故障诊断功能
4. 可实现参数的在线修改和保存功能

## 6. 文件清单

| 文件名                     | 类型       | 描述                     |
|----------------------------|------------|--------------------------|
| FB_EngravingController.TcPOU | 功能块文件 | 主控制器功能块实现       |
| EngravingController_Design_Doc.md | 设计文档 | 完整设计方案说明         |
| GVL_EngravingParameters.TcGVL | 全局变量表 | 可选的全局参数配置       |
| ST_DesignParameters.TcDUT  | 数据类型文件 | 可选的参数结构体定义     |

## 7. 使用示例

### 在主程序中调用
```st
PROGRAM MAIN
VAR
    EngravingCtrl : FB_EngravingController;
    HMI_DesignSelect : INT := 1; // HMI设计选择输入
    HMI_Depth : REAL := 0.0;     // HMI深度输入（备用）
    HMI_Speed : REAL := 0.0;     // HMI速度输入（备用）
    Axis_Z_Enable : BOOL;        // Z轴电机驱动输入
    Spindle_Enable : BOOL;       // 雕刻主轴驱动输入
END_VAR

// 调用雕刻控制器功能块
EngravingCtrl(
    DesignSelection := HMI_DesignSelect,
    EngravingDepth := HMI_Depth,
    EngravingSpeed := HMI_Speed,
    ZAxisMotor => Axis_Z_Enable,
    EngravingMotor => Spindle_Enable
);
```