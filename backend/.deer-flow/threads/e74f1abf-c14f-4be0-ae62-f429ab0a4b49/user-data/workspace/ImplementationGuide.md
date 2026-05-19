# Multi-Level Parking Lot Automation System
## Implementation Guide

### 1.需求分析

#### 核心功能需求
1. **入口闸门管理**
   - 检测车辆到达信号
   - 分配第一个可用车位（1-100号）
   - 标记车位为占用状态
   - 输出分配的车位号
   - 已分配或取车中的车位不能重复分配

2. **出口闸门管理**
   - 检测车辆离开信号
   - 释放对应车位
   - 重置车位号状态

3. **取车管理**
   - 检测取车请求
   - 设置取车中标志
   - 调用车辆移动函数
   - 完成后释放车位
   - 重置标志和车位号

4. **车位跟踪**
   - 维护100个车位的布尔状态数组
   - 实时更新车位占用状态

5. **车辆移动**
   - 实现MoveCarToExitGate函数
   - 返回操作成功状态

#### 形式化验证属性
1. 安全属性：不允许双重停车
2. 安全属性：满位时禁止车辆进入
3. 活性属性：入口请求总会得到响应
4. 安全属性：只能对已停放车辆发起取车请求
5. 活性属性：取车操作总会完成
6. 安全属性：车辆移动操作互斥
7. 安全属性：只有已释放车位的车辆才能离开
8. 安全关键属性：紧急停止可中断所有操作

### 2.架构设计

#### 整体架构描述
本系统采用模块化分层架构设计，主要分为以下层次：
- **硬件接口层**：处理与传感器、执行器的信号交互
- **控制逻辑层**：实现核心业务逻辑和状态管理
- **应用功能层**：提供对外的功能接口和服务
- **监控管理层**：实现系统状态监控和故障诊断

#### 模块划分
```
┌───────────────────┐
│   监控管理层      │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│   应用功能层      │
│  ┌─────────────┐  │
│  │ 入口管理模块 │  │
│  ├─────────────┤  │
│  │ 出口管理模块 │  │
│  ├─────────────┤  │
│  │ 取车管理模块 │  │
│  └─────────────┘  │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│   控制逻辑层      │
│  ┌─────────────┐  │
│  │ 车位管理模块 │  │
│  ├─────────────┤  │
│  │ 车辆移动模块 │  │
│  ├─────────────┤  │
│  │ 状态机管理   │  │
│  └─────────────┘  │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│   硬件接口层      │
└───────────────────┘
```

### 3.功能块设计

#### FB_ParkingLotManagement - 主功能块
**功能描述**：实现停车场管理的核心逻辑，包括入口控制、出口控制、取车管理和车位状态维护

| 参数类型 | 参数名称 | 数据类型 | 描述 |
|---------|---------|---------|------|
| 输入 | i_EntryVehicleDetect | BOOL | 入口车辆检测信号 |
| 输入 | i_ExitVehicleDetect | BOOL | 出口车辆检测信号 |
| 输入 | i_PickupRequest | BOOL | 取车请求信号 |
| 输入 | i_PickupCarID | UINT | 取车请求对应的车辆ID |
| 输出 | o_EntryGateOpen | BOOL | 入口闸门打开命令 |
| 输出 | o_ExitGateOpen | BOOL | 出口闸门打开命令 |
| 输出 | o_AssignedParkingSpot | UINT | 分配的车位号（0表示无可用车位） |
| 输出 | o_PickupInProgress | BOOL | 取车操作进行中标志 |
| 输出 | o_PickupSuccess | BOOL | 取车操作成功状态 |
| 输出 | o_ParkingSpotStatus | ARRAY[1..100] OF BOOL | 车位状态数组（TRUE表示占用） |

**内部变量**：
- ParkingSpots: ARRAY[1..100] OF BOOL - 内部车位状态跟踪
- CarSpotMapping: ARRAY[1..100] OF UINT - 车辆ID到车位的映射
- NextAvailableSpot: UINT - 下一个可用车位索引
- PickupInProgress: BOOL - 内部取车进行中标志
- PickupTargetSpot: UINT - 取车目标车位
- MoveCarResult: BOOL - 车辆移动函数返回结果

**方法**：
- FindNextAvailableSpot(): UINT - 查找第一个可用车位
- AssignParkingSpot(): UINT - 分配可用车位
- ReleaseParkingSpot(SpotNumber: UINT) - 释放指定车位
- GetNextCarID(): UINT - 生成下一个车辆ID

#### MoveCarToExitGate - 车辆移动函数
**功能描述**：控制车辆从指定车位移动到出口闸门

| 参数类型 | 参数名称 | 数据类型 | 描述 |
|---------|---------|---------|------|
| 输入 | i_SpotNumber | UINT | 要移动车辆的车位号 |
| 返回值 | MoveCarToExitGate | BOOL | 移动操作成功状态 |

### 4.数据结构设计

#### ParkingSpotStatus 结构体
```st
TYPE ParkingSpotStatus :
STRUCT
    SpotNumber : UINT;           // 车位编号
    IsOccupied : BOOL;           // 车位占用状态
    CarID : UINT;                // 停放车辆ID
    LastUpdated : DT;            // 状态最后更新时间
END_STRUCT
END_TYPE
```

#### 全局变量定义
```st
GVL_GlobalVariables
VAR_GLOBAL
    g_ParkingLotStatus : ARRAY[1..100] OF ParkingSpotStatus; // 全局车位状态
    g_AvailableSpots : UINT;                                // 可用车位数量
    g_TotalSpots : UINT := 100;                             // 总车位数
    g_EmergencyStop : BOOL;                                 // 紧急停止信号
    g_SystemStatus : UINT;                                  // 系统运行状态
END_VAR
```

### 5.实现建议

#### 开发环境建议
- 使用Beckhoff TwinCAT 3作为PLC开发环境
- 采用结构化文本(ST)语言编写逻辑
- 使用TwinCAT Scope View进行调试和监控

#### 部署建议
- 采用冗余PLC配置提高系统可用性
- 实现分布式I/O架构减少布线复杂度
- 使用工业以太网(EtherCAT)作为现场总线

#### 安全建议
- 所有输入信号都应进行故障安全处理
- 关键操作应实现双重确认机制
- 定期备份程序和配置文件

#### 性能优化建议
- 实现车位查找算法的优化（如使用位掩码）
- 采用状态机模式管理系统状态
- 实现数据缓存机制减少重复计算

### 6.文件清单

| 文件名 | 描述 |
|-------|------|
| FB_ParkingLotManagement.TcPOU | 停车场管理主功能块 |
| MoveCarToExitGate.TcPOU | 车辆移动控制函数 |
| ParkingLot_ValidationSpecs.txt | 形式化验证规格说明 |
| ImplementationGuide.md | 系统实现指南 |
| GVL_GlobalVariables.TcGVL | 全局变量定义 |
| Types_ParkingLot.TcDUT | 数据类型定义 |
| FB_EntryGateControl.TcPOU | 入口闸门控制功能块 |
| FB_ExitGateControl.TcPOU | 出口闸门控制功能块 |
| FB_VehicleDetection.TcPOU | 车辆检测处理功能块 |
| ParkingLot_HMI_Config.TcHmi | HMI界面配置文件 |
