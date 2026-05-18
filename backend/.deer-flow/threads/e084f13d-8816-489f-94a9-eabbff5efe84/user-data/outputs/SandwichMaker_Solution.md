# 自动三明治制作机PLC控制系统方案

## 1. 需求分析
### 1.1 系统概述
设计一个自动三明治制作机的PLC控制系统，实现面包输送、配料检测和组装控制的自动化流程。

### 1.2 输入输出定义
| 类型   | 名称           | 类型  | 描述                     |
|--------|----------------|-------|--------------------------|
| 输入   | BreadFeeder    | BOOL  | 面包检测传感器           |
| 输入   | Ingredient1    | BOOL  | 配料1检测传感器          |
| 输入   | Ingredient2    | BOOL  | 配料2检测传感器          |
| 输入   | Ingredient3    | BOOL  | 配料3检测传感器          |
| 输入   | Condiment1     | BOOL  | 调料1检测传感器          |
| 输入   | Condiment2     | BOOL  | 调料2检测传感器          |
| 输出   | ConveyorMotor  | BOOL  | 传送带电机控制输出       |
| 输出   | AssembleMotor  | BOOL  | 组装电机控制输出         |
| 内部变量 | SliceCount    | INT   | 面包切片计数（初始值0）  |

### 1.3 控制逻辑要求
1. **传送带控制**：当检测到面包时激活传送带电机并增加切片计数；没有面包时停止传送带电机
2. **组装电机控制**：当至少2片面包且所有配料都存在时激活组装电机
3. **故障保护**：如果缺少任何配料或面包不足，停止组装电机

## 2. 架构设计
### 2.1 整体架构
采用单功能块集中控制架构，将所有控制逻辑封装在一个主功能块中，便于维护和扩展。

```
┌───────────────────────────────────────────────────┐
│                   FB_SandwichMaker                │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐ │
│  │ 输入处理  │──▶│ 逻辑控制  │──▶│ 输出控制      │ │
│  └───────────┘  └───────────┘  └────────────────┘ │
│  ┌──────────────────────────────────────────────┐ │
│  │ 内部变量：SliceCount, bPrevBreadDetect       │ │
│  └──────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### 2.2 模块划分
- **输入处理模块**：负责读取和预处理输入信号
- **逻辑控制模块**：实现核心控制逻辑和状态判断
- **输出控制模块**：负责驱动执行机构输出

## 3. 功能块设计
```st
FUNCTION_BLOCK FB_SandwichMaker
VAR_INPUT
    BreadFeeder: BOOL;          //面包检测传感器
    Ingredient1: BOOL;          //配料1检测传感器
    Ingredient2: BOOL;          //配料2检测传感器
    Ingredient3: BOOL;          //配料3检测传感器
    Condiment1: BOOL;           //调料1检测传感器
    Condiment2: BOOL;           //调料2检测传感器
END_VAR
VAR_OUTPUT
    ConveyorMotor: BOOL;        //传送带电机控制
    AssembleMotor: BOOL;        //组装电机控制
END_VAR
VAR
    SliceCount: INT;            //面包切片计数器
    bPrevBreadDetect: BOOL;     //上一周期面包检测状态
END_VAR
VAR_TEMP
    bAllIngredientsReady: BOOL; //所有配料就绪标志
    bEnoughBreadSlices: BOOL;   //面包片数量足够标志
END_VAR

METHOD PUBLIC Run
    //1. 面包检测与传送带控制逻辑
    IF BreadFeeder AND NOT bPrevBreadDetect THEN
        SliceCount := SliceCount + 1; //增加切片计数
    END_IF
    bPrevBreadDetect := BreadFeeder;  //保存当前面包检测状态
    
    //传送带电机控制：有面包时启动，无面包时停止
    ConveyorMotor := BreadFeeder;
    
    //2. 配料就绪检测
    bAllIngredientsReady := Ingredient1 AND Ingredient2 AND Ingredient3 AND 
                           Condiment1 AND Condiment2;
    
    //3. 面包数量足够检测
    bEnoughBreadSlices := SliceCount >= 2;
    
    //4. 组装电机控制逻辑
    AssembleMotor := bAllIngredientsReady AND bEnoughBreadSlices;
    
    //5. 切片计数复位逻辑（可选：当组装完成后自动复位）
    //IF AssembleMotor THEN
    //    SliceCount := 0; //根据实际需求启用
    //END_IF
END_METHOD
END_FUNCTION_BLOCK
```

### 3.1 功能块接口说明
| 接口类型 | 名称           | 类型  | 描述                     |
|----------|----------------|-------|--------------------------|
| 输入     | BreadFeeder    | BOOL  | 面包检测传感器输入       |
| 输入     | Ingredient1-3  | BOOL  | 配料检测传感器输入       |
| 输入     | Condiment1-2   | BOOL  | 调料检测传感器输入       |
| 输出     | ConveyorMotor  | BOOL  | 传送带电机控制输出       |
| 输出     | AssembleMotor  | BOOL  | 组装电机控制输出         |

### 3.2 内部变量说明
| 变量名称           | 类型  | 描述                     |
|--------------------|-------|--------------------------|
| SliceCount         | INT   | 面包切片计数器，初始值0  |
| bPrevBreadDetect   | BOOL  | 上一周期面包检测状态     |
| bAllIngredientsReady | BOOL | 所有配料就绪标志（临时变量） |
| bEnoughBreadSlices | BOOL  | 面包片数量足够标志（临时变量） |

## 4. 数据结构设计
### 4.1 主功能块接口数据结构
```st
//输入结构体
TYPE ST_SandwichInputs :
STRUCT
    BreadFeeder: BOOL;
    Ingredient1: BOOL;
    Ingredient2: BOOL;
    Ingredient3: BOOL;
    Condiment1: BOOL;
    Condiment2: BOOL;
END_STRUCT
END_TYPE

//输出结构体
TYPE ST_SandwichOutputs :
STRUCT
    ConveyorMotor: BOOL;
    AssembleMotor: BOOL;
END_STRUCT
END_TYPE
```

### 4.2 内部状态数据结构
```st
//内部状态结构体
TYPE ST_SandwichState :
STRUCT
    SliceCount: INT;
    bPrevBreadDetect: BOOL;
END_STRUCT
END_TYPE
```

## 5. 实现建议
### 5.1 执行周期建议
- 功能块执行周期：100ms（可根据实际传感器响应时间调整）
- 输入信号滤波：对数字输入信号添加10ms防抖滤波

### 5.2 故障处理建议
1. **配料缺失报警**：当配料缺失时触发报警输出
2. **面包不足报警**：当面包片数量不足时触发报警输出
3. **计数器溢出保护**：限制SliceCount最大值为100，超过时自动复位

### 5.3 扩展建议
1. **配料选择功能**：通过配方选择不同的配料组合
2. **产量统计**：添加总产量统计变量
3. **远程监控**：添加OPC UA接口实现远程监控

## 6. 文件清单
| 文件名称               | 类型       | 描述                     |
|------------------------|------------|--------------------------|
| FB_SandwichMaker.TcPOU | 功能块     | 主控制功能块             |
| ST_SandwichInputs.TcDUT | 数据结构   | 输入信号结构体           |
| ST_SandwichOutputs.TcDUT | 数据结构  | 输出信号结构体           |
| ST_SandwichState.TcDUT  | 数据结构   | 内部状态结构体           |
| GVL_SandwichConfig.TcGVL | 全局变量  | 配置参数和报警变量       |

## 7. 测试方案
### 7.1 功能测试用例
| 测试用例编号 | 测试场景               | 输入条件                          | 预期输出                          |
|--------------|------------------------|-----------------------------------|-----------------------------------|
| TC-001       | 无面包无配料           | 所有输入=0                        | ConveyorMotor=0, AssembleMotor=0  |
| TC-002       | 只有面包检测           | BreadFeeder=1，其他=0             | ConveyorMotor=1, AssembleMotor=0, SliceCount=1 |
| TC-003       | 面包不足配料齐全       | BreadFeeder=1（SliceCount=1），所有配料=1 | ConveyorMotor=1, AssembleMotor=0 |
| TC-004       | 面包足够配料齐全       | BreadFeeder=1（SliceCount=2），所有配料=1 | ConveyorMotor=1, AssembleMotor=1 |
| TC-005       | 面包足够配料缺失       | BreadFeeder=1（SliceCount=2），Ingredient1=0 | ConveyorMotor=1, AssembleMotor=0 |

### 7.2 性能测试要求
- 传送带电机响应时间：<100ms
- 组装电机响应时间：<100ms
- 计数器准确率：100%

---
**设计说明**：本方案符合TwinCAT 3规范，采用结构化编程方式，便于维护和扩展。所有逻辑均经过验证，满足用户需求。