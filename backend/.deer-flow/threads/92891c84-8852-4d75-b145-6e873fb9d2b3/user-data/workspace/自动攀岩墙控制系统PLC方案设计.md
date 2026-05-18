# 自动攀岩墙控制系统PLC方案设计

## 1. 需求分析

### 1.1 系统概述
本系统为自动攀岩墙控制系统，主要实现以下功能：
- 根据用户体重自动调整攀岩墙电机速度
- 根据选择的攀岩路线自动设置难度等级
- 根据墙的高度自动控制照明系统

### 1.2 输入变量
- `UserWeightSensor (REAL)`：测量用户体重
- `WallDifficultyLevel (INT)`：初始难度等级设置（将由路线选择覆盖）
- `WallHeight (REAL)`：墙的高度定义
- `RouteSelector (INT)`：选择攀岩路线（1、2、3）

### 1.3 输出变量
- `ClimbingMotorSpeed (REAL)`：控制攀岩墙电机速度
- `WallLights (BOOL)`：控制墙的照明系统

### 1.4 核心逻辑
1. **电机速度调整**：用户体重>60kg时设为1.0，≤60kg时设为0.8
2. **难度等级设置**：Route1对应等级1，Route2对应等级2，Route3对应等级3
3. **墙灯控制**：高度>5.0米时激活（TRUE），否则关闭（FALSE）

### 1.5 形式化属性要求
- 若`UserWeightSensor > 60.0`，则`ClimbingMotorSpeed`必须等于1.0
- 若`RouteSelector = 1`，则`WallDifficultyLevel`必须等于1
- 若`RouteSelector = 2`，则`WallDifficultyLevel`必须等于2
- 若`RouteSelector = 3`，则`WallDifficultyLevel`必须等于3
- 若`WallHeight > 5.0`，则`WallLights`必须等于TRUE

## 2. 架构设计

### 2.1 整体架构
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   输入模块          │    │   核心控制功能块    │    │   输出模块          │
│ Inputs             │───▶│ FB_ClimbingWallCtrl │───▶│ Outputs            │
│ - UserWeightSensor │    │                     │    │ - ClimbingMotorSpeed│
│ - WallHeight       │    │                     │    │ - WallLights        │
│ - RouteSelector    │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         ▲                          │                          ▲
         │                          │                          │
         │                          ▼                          │
         │                    ┌─────────────────────┐          │
         │                    │   数据存储区        │          │
         │                    │ GVL_ClimbingSystem  │          │
         │                    │ - WallDifficultyLevel│         │
         │                    └─────────────────────┘          │
         │                          ▲                          │
         └──────────────────────────┘──────────────────────────┘
```

### 2.2 模块划分
1. **输入模块**：负责采集所有外部输入信号
2. **核心控制功能块**：实现主要控制逻辑
3. **输出模块**：负责控制执行器
4. **全局变量列表**：存储系统状态参数

## 3. 功能块设计

### 3.1 核心控制功能块 `FB_ClimbingWallCtrl`

```st
FUNCTION_BLOCK FB_ClimbingWallCtrl
VAR_INPUT
    UserWeightSensor : REAL;  // 用户体重传感器输入
    WallHeight : REAL;        // 墙的高度输入
    RouteSelector : INT;      // 路线选择输入
END_VAR
VAR_OUTPUT
    ClimbingMotorSpeed : REAL;  // 电机速度输出
    WallLights : BOOL;          // 墙灯控制输出
END_VAR
VAR_IN_OUT
    WallDifficultyLevel : INT;  // 难度等级（双向变量，可被外部设置或内部修改）
END_VAR
VAR
    // 内部变量
END_VAR
```

#### 功能描述
实现所有核心控制逻辑：
- 根据用户体重计算电机速度
- 根据路线选择设置难度等级
- 根据墙高控制照明系统

#### 逻辑实现
```st
// 1. 电机速度控制逻辑
IF UserWeightSensor > 60.0 THEN
    ClimbingMotorSpeed := 1.0;
ELSE
    ClimbingMotorSpeed := 0.8;
END_IF

// 2. 难度等级控制逻辑
CASE RouteSelector OF
    1: WallDifficultyLevel := 1;
    2: WallDifficultyLevel := 2;
    3: WallDifficultyLevel := 3;
    ELSE
        // 保持当前难度等级或设置默认值
END_CASE

// 3. 墙灯控制逻辑
WallLights := (WallHeight > 5.0);
```

## 4. 数据结构设计

### 4.1 全局变量列表 `GVL_ClimbingSystem`

```st
GVL_ClimbingSystem
VAR_GLOBAL
    // 系统状态变量
    WallDifficultyLevel : INT := 1;  // 默认难度等级为1
    
    // 系统配置参数
    MIN_WEIGHT_FOR_FULL_SPEED : REAL := 60.0;  // 满速体重阈值
    MIN_HEIGHT_FOR_LIGHTS : REAL := 5.0;       // 开灯高度阈值
    
    // 路线难度映射
    ROUTE1_DIFFICULTY : INT := 1;
    ROUTE2_DIFFICULTY : INT := 2;
    ROUTE3_DIFFICULTY : INT := 3;
END_VAR
```

### 4.2 类型定义

```st
TYPE ET_RouteSelector :
    (Route1 := 1,
     Route2 := 2,
     Route3 := 3);
END_TYPE

TYPE ST_ClimbingSystemStatus :
    STRUCT
        CurrentWeight : REAL;
        CurrentHeight : REAL;
        CurrentRoute : ET_RouteSelector;
        CurrentDifficulty : INT;
        MotorSpeed : REAL;
        LightsActive : BOOL;
    END_STRUCT;
END_TYPE
```

## 5. 实现建议

### 5.1 实现步骤
1. 创建全局变量列表 `GVL_ClimbingSystem`
2. 创建功能块 `FB_ClimbingWallCtrl`
3. 在主程序中调用功能块
4. 添加诊断和错误处理逻辑
5. 实现输入输出映射

### 5.2 主程序调用示例

```st
PROGRAM MAIN
VAR
    fbClimbingCtrl : FB_ClimbingWallCtrl;
    
    // 输入变量
    i_UserWeightSensor : REAL;
    i_WallHeight : REAL;
    i_RouteSelector : INT;
    
    // 输出变量
    q_ClimbingMotorSpeed : REAL;
    q_WallLights : BOOL;
END_VAR

// 调用核心控制功能块
fbClimbingCtrl(
    UserWeightSensor := i_UserWeightSensor,
    WallHeight := i_WallHeight,
    RouteSelector := i_RouteSelector,
    ClimbingMotorSpeed => q_ClimbingMotorSpeed,
    WallLights => q_WallLights,
    WallDifficultyLevel => GVL_ClimbingSystem.WallDifficultyLevel
);
```

### 5.3 诊断与错误处理建议
```st
// 在功能块中添加错误处理
VAR
    ErrorCode : INT := 0;
    ErrorMsg : STRING(80);
END_VAR

// 输入范围检查
IF RouteSelector < 1 OR RouteSelector > 3 THEN
    ErrorCode := 1;
    ErrorMsg := 'Invalid route selection';
    // 设置默认值
    RouteSelector := 1;
END_IF

IF UserWeightSensor < 0 OR UserWeightSensor > 200 THEN
    ErrorCode := 2;
    ErrorMsg := 'Invalid weight value';
    // 设置安全值
    ClimbingMotorSpeed := 0.8;
END_IF
```

## 6. 文件清单

| 文件名                  | 类型          | 描述                          |
|-------------------------|---------------|-------------------------------|
| `GVL_ClimbingSystem.TcGVL` | 全局变量列表  | 存储系统状态和配置参数        |
| `FB_ClimbingWallCtrl.TcPOU` | 功能块        | 核心控制逻辑实现              |
| `ET_RouteSelector.TcDUT`   | 枚举类型      | 路线选择枚举定义              |
| `ST_ClimbingSystemStatus.TcDUT` | 结构体类型  | 系统状态结构体定义            |
| `MAIN.TcPOU`            | 主程序        | 系统主入口                    |
| `IO_Mapping.TcPOU`      | 程序          | 输入输出映射程序              |

## 7. 形式化属性验证

### 7.1 属性验证实现
```st
// 在功能块中添加属性验证
METHOD ValidateProperties : BOOL
VAR
    Result : BOOL := TRUE;
END_VAR

// 属性1：若UserWeightSensor > 60.0，则ClimbingMotorSpeed必须等于1.0
IF UserWeightSensor > 60.0 AND ClimbingMotorSpeed <> 1.0 THEN
    Result := FALSE;
    // 记录错误
END_IF

// 属性2：若RouteSelector = 1，则WallDifficultyLevel必须等于1
IF RouteSelector = 1 AND WallDifficultyLevel <> 1 THEN
    Result := FALSE;
    // 记录错误
END_IF

// 属性3：若RouteSelector = 2，则WallDifficultyLevel必须等于2
IF RouteSelector = 2 AND WallDifficultyLevel <> 2 THEN
    Result := FALSE;
    // 记录错误
END_IF

// 属性4：若RouteSelector = 3，则WallDifficultyLevel必须等于3
IF RouteSelector = 3 AND WallDifficultyLevel <> 3 THEN
    Result := FALSE;
    // 记录错误
END_IF

// 属性5：若WallHeight > 5.0，则WallLights必须等于TRUE
IF WallHeight > 5.0 AND NOT WallLights THEN
    Result := FALSE;
    // 记录错误
END_IF

ValidateProperties := Result;
END_METHOD
```

### 7.2 验证调用
在主程序中定期调用验证方法：
```st
// 定期验证属性
IF fbClimbingCtrl.ValidateProperties() = FALSE THEN
    // 触发警报或进入安全状态
END_IF
```