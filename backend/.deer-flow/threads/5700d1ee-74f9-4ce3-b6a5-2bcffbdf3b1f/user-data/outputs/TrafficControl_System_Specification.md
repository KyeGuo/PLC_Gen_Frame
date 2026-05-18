# 智能道路交通管理系统PLC方案设计

## 1. 需求分析

### 功能需求
- 监控四个交叉路口的实时车辆数量
- 独立管理两对交叉路口（1&2，3&4）的交通灯状态
- 根据车辆数量动态调整交通灯优先级：车辆较多的路口优先放行
- 保证相对交叉路口的交通灯状态互补（一个绿灯，另一个必为红灯）
- 实时响应车辆数量变化，动态更新交通灯状态

### 形式化属性要求
1. 当VehicleCount1 > VehicleCount2时，TrafficLight1为绿色且TrafficLight2为红色
2. 当VehicleCount2 >= VehicleCount1时，TrafficLight2为绿色且TrafficLight1为红色
3. 当VehicleCount3 > VehicleCount4时，TrafficLight3为绿色且TrafficLight4为红色
4. 当VehicleCount4 >= VehicleCount3时，TrafficLight4为绿色且TrafficLight3为红色
5. TrafficLight1和TrafficLight2始终处于相反状态
6. TrafficLight3和TrafficLight4始终处于相反状态

## 2. 架构设计

### 整体架构
```
┌───────────────────┐    ┌───────────────────┐
│   车辆检测系统     │───▶│   PLC控制系统     │───▶│   交通灯执行系统   │
│ (VehicleCount1-4) │    │  FB_TrafficControl│    │ (TrafficLight1-4) │
└───────────────────┘    └───────────────────┘    └───────────────────┘
```

### 模块划分
1. **数据采集层**：负责采集四个交叉路口的车辆数量数据
2. **控制逻辑层**：通过FB_TrafficControl功能块实现交通灯控制逻辑
3. **执行输出层**：根据控制信号驱动交通灯设备

## 3. 功能块设计

### FB_TrafficControl - 交通控制功能块

#### 功能描述
实现两对交叉路口的交通灯智能控制，根据实时车辆数量动态调整放行优先级，保证相对路口的灯状态互补。

#### 输入参数
| 参数名称       | 类型 | 描述               |
|----------------|------|--------------------|
| VehicleCount1  | INT  | 交叉路口1的车辆数量 |
| VehicleCount2  | INT  | 交叉路口2的车辆数量 |
| VehicleCount3  | INT  | 交叉路口3的车辆数量 |
| VehicleCount4  | INT  | 交叉路口4的车辆数量 |

#### 输出参数
| 参数名称       | 类型 | 描述               |
|----------------|------|--------------------|
| TrafficLight1  | BOOL | 交叉路口1交通灯状态（TRUE=绿灯，FALSE=红灯） |
| TrafficLight2  | BOOL | 交叉路口2交通灯状态（TRUE=绿灯，FALSE=红灯） |
| TrafficLight3  | BOOL | 交叉路口3交通灯状态（TRUE=绿灯，FALSE=红灯） |
| TrafficLight4  | BOOL | 交叉路口4交通灯状态（TRUE=绿灯，FALSE=红灯） |

#### 内部变量
| 变量名称       | 类型 | 描述               |
|----------------|------|--------------------|
| Group1Green    | BOOL | 第一组绿灯状态标志  |
| Group2Green    | BOOL | 第二组绿灯状态标志  |

## 4. 数据结构设计

### 交通灯控制结构体
```st
TYPE ST_TrafficGroup :
STRUCT
    VehicleCountA : INT;      // A路口车辆数量
    VehicleCountB : INT;      // B路口车辆数量
    TrafficLightA : BOOL;     // A路口交通灯状态
    TrafficLightB : BOOL;     // B路口交通灯状态
END_STRUCT
END_TYPE
```

### 系统状态结构体
```st
TYPE ST_TrafficSystemState :
STRUCT
    Group1 : ST_TrafficGroup; // 第一组交叉路口状态
    Group2 : ST_TrafficGroup; // 第二组交叉路口状态
END_STRUCT
END_TYPE
```

## 5. 实现建议

### 逻辑实现要点
1. **独立分组处理**：将两对交叉路口的控制逻辑完全分离，提高系统模块化程度
2. **互补状态保证**：通过`NOT`操作确保相对路口的灯状态始终相反
3. **优先级判断**：使用简单的比较运算实现车辆数量优先级判断
4. **实时响应**：每个扫描周期都重新计算交通灯状态，确保实时响应车辆数量变化

### 性能优化
- 避免使用复杂的数学运算，保证逻辑执行效率
- 内部变量使用BOOL类型，减少内存占用
- 采用结构化编程，提高代码可读性和维护性

### 扩展建议
- 添加车辆数量变化率检测，实现预测性控制
- 增加最小绿灯时间限制，避免交通灯频繁切换
- 集成时间控制模式，在特定时段采用固定配时方案
- 添加故障诊断功能，检测车辆检测器和交通灯设备故障

## 6. 文件清单

| 文件名称                | 类型        | 描述                     |
|-------------------------|-------------|--------------------------|
| FB_TrafficControl.TcPOU | PLC功能块   | 交通控制核心逻辑实现     |
| ST_TrafficGroup.TcDUT   | 数据类型    | 交通组状态结构体         |
| ST_TrafficSystemState.TcDUT | 数据类型 | 系统整体状态结构体       |
| GVL_TrafficControl.TcGVL | 全局变量表  | 系统全局变量定义         |
| TrafficControl_Main.TcPOU | 主程序     | 系统主控制逻辑           |