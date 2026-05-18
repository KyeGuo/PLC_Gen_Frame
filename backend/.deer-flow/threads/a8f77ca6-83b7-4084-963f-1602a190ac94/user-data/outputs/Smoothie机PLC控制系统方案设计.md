# 自动Smoothie机PLC控制系统方案设计

## 1. 需求分析

### 1.1 功能需求
根据用户需求，自动Smoothie机控制系统需要实现以下功能：
- 支持3种不同的Smoothie食谱选择
- 在搅拌开始前自动检查所需原料的可用性
- 只有当选择有效且所有原料可用时，才激活搅拌电机和分配器
- 否则关闭所有输出

### 1.2 输入变量定义
| 变量名称 | 类型 | 描述 |
|---------|------|------|
| BananaAvailable | BOOL | 香蕉原料是否可用（True=可用，False=不可用） |
| BerryMixAvailable | BOOL | 混合莓原料是否可用（True=可用，False=不可用） |
| SpinachAvailable | BOOL | 菠菜原料是否可用（True=可用，False=不可用） |
| YogurtAvailable | BOOL | 酸奶原料是否可用（True=可用，False=不可用） |
| CustomerPreference | INT | 用户选择的食谱（1=食谱1，2=食谱2，3=食谱3） |

### 1.3 输出变量定义
| 变量名称 | 类型 | 描述 |
|---------|------|------|
| BlenderMotor | BOOL | 搅拌电机控制（True=启动，False=停止） |
| Dispenser | BOOL | 分配器控制（True=激活，False=关闭） |

### 1.4 食谱定义
| 食谱编号 | 所需原料 |
|---------|---------|
| 1 | 香蕉、混合莓、酸奶 |
| 2 | 混合莓、菠菜、酸奶 |
| 3 | 香蕉、菠菜、酸奶 |

## 2. 架构设计

### 2.1 整体架构描述
本系统采用模块化设计，主要包含以下模块：
1. **主控制模块**：负责协调各个功能块的工作
2. **原料检查功能块**：根据选择的食谱检查所需原料是否可用
3. **输出控制功能块**：根据原料检查结果控制搅拌电机和分配器
4. **状态监控模块**：监控系统状态和原料可用性

### 2.2 架构图描述
```
用户输入 → 主控制模块 → 原料检查功能块 → 输出控制功能块 → 执行机构
    ↑                      ↓
    └─── 状态监控模块 ←────┘
```

### 2.3 模块划分
1. **FB_SmoothieController**：主控制功能块，整合所有功能
2. **FB_IngredientChecker**：原料检查功能块，检查所选食谱的原料是否齐全
3. **FC_RecipeSelector**：食谱选择函数，根据用户选择返回所需原料组合

## 3. 功能块设计

### 3.1 FB_IngredientChecker（原料检查功能块）
```st
FUNCTION_BLOCK FB_IngredientChecker
VAR_INPUT
    BananaAvailable: BOOL;
    BerryMixAvailable: BOOL;
    SpinachAvailable: BOOL;
    YogurtAvailable: BOOL;
    RequiredBanana: BOOL;
    RequiredBerryMix: BOOL;
    RequiredSpinach: BOOL;
    RequiredYogurt: BOOL;
END_VAR
VAR_OUTPUT
    AllIngredientsAvailable: BOOL;
    MissingIngredients: STRING[100]; // 显示缺少的原料
END_VAR
VAR
    Missing: STRING[100];
END_VAR

METHOD CheckIngredients:
    Missing := '';
    
    IF RequiredBanana AND NOT BananaAvailable THEN
        Missing := Missing + '香蕉, ';
    END_IF;
    
    IF RequiredBerryMix AND NOT BerryMixAvailable THEN
        Missing := Missing + '混合莓, ';
    END_IF;
    
    IF RequiredSpinach AND NOT SpinachAvailable THEN
        Missing := Missing + '菠菜, ';
    END_IF;
    
    IF RequiredYogurt AND NOT YogurtAvailable THEN
        Missing := Missing + '酸奶, ';
    END_IF;
    
    IF LEN(Missing) > 0 THEN
        MissingIngredients := LEFT(Missing, LEN(Missing) - 2); // 移除最后一个逗号和空格
        AllIngredientsAvailable := FALSE;
    ELSE
        MissingIngredients := '所有原料齐全';
        AllIngredientsAvailable := TRUE;
    END_IF;
END_METHOD
```

### 3.2 FC_RecipeSelector（食谱选择函数）
```st
FUNCTION FC_RecipeSelector: ST
VAR_INPUT
    CustomerPreference: INT;
END_VAR
VAR_OUTPUT
    RequiredBanana: BOOL;
    RequiredBerryMix: BOOL;
    RequiredSpinach: BOOL;
    RequiredYogurt: BOOL;
    ValidRecipe: BOOL;
END_VAR

CASE CustomerPreference OF
    1: // 食谱1: 香蕉、混合莓、酸奶
        RequiredBanana := TRUE;
        RequiredBerryMix := TRUE;
        RequiredSpinach := FALSE;
        RequiredYogurt := TRUE;
        ValidRecipe := TRUE;
    
    2: // 食谱2: 混合莓、菠菜、酸奶
        RequiredBanana := FALSE;
        RequiredBerryMix := TRUE;
        RequiredSpinach := TRUE;
        RequiredYogurt := TRUE;
        ValidRecipe := TRUE;
    
    3: // 食谱3: 香蕉、菠菜、酸奶
        RequiredBanana := TRUE;
        RequiredBerryMix := FALSE;
        RequiredSpinach := TRUE;
        RequiredYogurt := TRUE;
        ValidRecipe := TRUE;
    
    ELSE: // 无效选择
        RequiredBanana := FALSE;
        RequiredBerryMix := FALSE;
        RequiredSpinach := FALSE;
        RequiredYogurt := FALSE;
        ValidRecipe := FALSE;
END_CASE;

END_FUNCTION
```

### 3.3 FB_SmoothieController（主控制功能块）
```st
FUNCTION_BLOCK FB_SmoothieController
VAR_INPUT
    BananaAvailable: BOOL;
    BerryMixAvailable: BOOL;
    SpinachAvailable: BOOL;
    YogurtAvailable: BOOL;
    CustomerPreference: INT;
END_VAR
VAR_OUTPUT
    BlenderMotor: BOOL;
    Dispenser: BOOL;
    SystemStatus: STRING[50]; // 系统状态信息
END_VAR
VAR
    RecipeSelector: FC_RecipeSelector;
    IngredientChecker: FB_IngredientChecker;
    RequiredBanana: BOOL;
    RequiredBerryMix: BOOL;
    RequiredSpinach: BOOL;
    RequiredYogurt: BOOL;
    ValidRecipe: BOOL;
    AllIngredientsAvailable: BOOL;
    MissingIngredients: STRING[100];
END_VAR

// 选择食谱
RecipeSelector(
    CustomerPreference := CustomerPreference,
    RequiredBanana => RequiredBanana,
    RequiredBerryMix => RequiredBerryMix,
    RequiredSpinach => RequiredSpinach,
    RequiredYogurt => RequiredYogurt,
    ValidRecipe => ValidRecipe
);

// 检查原料可用性
IngredientChecker(
    BananaAvailable := BananaAvailable,
    BerryMixAvailable := BerryMixAvailable,
    SpinachAvailable := SpinachAvailable,
    YogurtAvailable := YogurtAvailable,
    RequiredBanana := RequiredBanana,
    RequiredBerryMix := RequiredBerryMix,
    RequiredSpinach := RequiredSpinach,
    RequiredYogurt := RequiredYogurt,
    AllIngredientsAvailable => AllIngredientsAvailable,
    MissingIngredients => MissingIngredients
);

// 控制输出
IF ValidRecipe AND AllIngredientsAvailable THEN
    BlenderMotor := TRUE;
    Dispenser := TRUE;
    SystemStatus := '正常运行中...';
ELSE
    BlenderMotor := FALSE;
    Dispenser := FALSE;
    IF NOT ValidRecipe THEN
        SystemStatus := '无效的食谱选择';
    ELSE
        SystemStatus := '缺少原料: ' + MissingIngredients;
    END_IF;
END_IF;

END_FUNCTION_BLOCK
```

## 4. 数据结构设计

### 4.1 食谱数据结构（可选扩展）
```st
TYPE RecipeData:STRUCT
    RecipeID: INT;
    RecipeName: STRING[50];
    RequiresBanana: BOOL;
    RequiresBerryMix: BOOL;
    RequiresSpinach: BOOL;
    RequiresYogurt: BOOL;
END_STRUCT;
END_TYPE

// 食谱数据库
VAR_GLOBAL
    RecipeDatabase: ARRAY[1..3] OF RecipeData := [
        (RecipeID := 1, RecipeName := '香蕉莓果酸奶', RequiresBanana := TRUE, RequiresBerryMix := TRUE, RequiresSpinach := FALSE, RequiresYogurt := TRUE),
        (RecipeID := 2, RecipeName := '绿能量', RequiresBanana := FALSE, RequiresBerryMix := TRUE, RequiresSpinach := TRUE, RequiresYogurt := TRUE),
        (RecipeID := 3, RecipeName := '香蕉菠菜酸奶', RequiresBanana := TRUE, RequiresBerryMix := FALSE, RequiresSpinach := TRUE, RequiresYogurt := TRUE)
    ];
END_VAR
```

## 5. 实现建议

### 5.1 程序实现步骤
1. 创建全局变量表，定义所有输入输出变量
2. 实现FC_RecipeSelector函数
3. 实现FB_IngredientChecker功能块
4. 实现FB_SmoothieController主控制功能块
5. 在主程序中调用FB_SmoothieController
6. 添加HMI界面，显示系统状态和原料信息

### 5.2 安全建议
- 添加紧急停止按钮，优先级最高
- 搅拌电机应配备过载保护
- 原料传感器应定期校准
- 添加门联锁保护，防止搅拌时打开机盖

### 5.3 维护建议
- 定期清洁原料传感器
- 监控搅拌电机运行时间，及时维护
- 记录原料消耗情况，实现自动补货提醒

## 6. 文件清单

| 文件名 | 类型 | 描述 |
|-------|------|------|
| GVL_SmoothieSystem.TcGVL | 全局变量列表 | 系统所有输入输出变量定义 |
| FC_RecipeSelector.TcPOU | 函数 | 食谱选择逻辑 |
| FB_IngredientChecker.TcPOU | 功能块 | 原料检查逻辑 |
| FB_SmoothieController.TcPOU | 功能块 | 主控制逻辑 |
| MAIN.TcPOU | 主程序 | 系统入口点 |
| RecipeData.TcDUT | 数据类型 | 食谱数据结构定义 |
| Smoothie机PLC控制系统方案设计.md | 文档 | 系统设计文档 |

## 7. 测试方案

### 7.1 功能测试
| 测试场景 | 输入条件 | 预期输出 |
|---------|---------|---------|
| 选择有效食谱且原料齐全 | CustomerPreference=1，所有Available=True | BlenderMotor=TRUE，Dispenser=TRUE |
| 选择有效食谱但缺少原料 | CustomerPreference=1，BananaAvailable=FALSE | BlenderMotor=FALSE，Dispenser=FALSE，显示"缺少原料: 香蕉" |
| 选择无效食谱 | CustomerPreference=4 | BlenderMotor=FALSE，Dispenser=FALSE，显示"无效的食谱选择" |
| 原料在运行中耗尽 | 运行中BananaAvailable变为FALSE | BlenderMotor=FALSE，Dispenser=FALSE |

### 7.2 边界测试
- 测试所有食谱的原料组合
- 测试无效的食谱选择值
- 测试原料从可用到不可用的切换
- 测试同时缺少多种原料的情况

## 8. 扩展建议

### 8.1 功能扩展
- 添加更多食谱选择
- 实现自定义食谱功能
- 添加原料消耗统计
- 实现远程监控和控制
- 添加语音交互功能

### 8.2 性能扩展
- 添加原料自动补货系统
- 实现多杯连续制作
- 添加口味浓度调节功能
- 实现Smoothie制作时间优化