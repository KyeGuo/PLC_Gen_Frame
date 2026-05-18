# FB_RequestHandler 功能块使用说明

## 1. 功能概述
FB_RequestHandler是一个状态机功能块，用于管理请求信号(request)、完成信号(done)和监听模式指示(listen)之间的状态转换逻辑。

## 2. 接口定义

### 输入变量
| 参数名 | 类型 | 描述 |
|-------|------|------|
| request | BOOL | 请求信号，触发状态转换从监听模式到处理模式 |
| done | BOOL | 完成信号，触发状态转换从处理模式回到监听模式 |

### 输出变量
| 参数名 | 类型 | 描述 |
|-------|------|------|
| listen | BOOL | 监听模式指示，TRUE表示当前处于监听状态，FALSE表示当前处于处理状态 |

## 3. 状态转换逻辑

### 状态0：监听模式
- 初始状态
- listen输出为TRUE
- 当request为TRUE时，转换到状态1，listen输出变为FALSE

### 状态1：处理模式
- listen输出为FALSE
- 当done为TRUE时，转换回状态0，listen输出变为TRUE

## 4. 形式化属性

1. 当系统在状态0且request为FALSE时，listen必须为TRUE
2. 当系统在状态0且request为TRUE且done为FALSE时，listen必须为FALSE且状态变为1
3. 当系统在状态1且done为FALSE时，保持状态1
4. 当系统在状态1且done为TRUE时，listen必须为TRUE且状态变为0

## 5. 使用示例

### 结构化文本示例
```st
VAR
    fbRequestHandler : FB_RequestHandler;
    
    // 外部输入
    userRequest : BOOL;
    processDone : BOOL;
    
    // 外部输出
    systemListening : BOOL;
END_VAR

// 调用功能块
fbRequestHandler(request := userRequest, done := processDone, listen => systemListening);

// 处理逻辑
IF NOT systemListening THEN
    // 执行处理任务
    // ...
    
    // 任务完成后设置processDone为TRUE
    processDone := TRUE;
END_IF;
```

### 梯形图示例
1. 将FB_RequestHandler功能块拖放到梯形图中
2. 连接输入变量request和done
3. 连接输出变量listen到需要的逻辑

## 6. 注意事项

1. done是输入变量，功能块内部不能设置其值，只能读取。需要由外部处理逻辑在任务完成时设置done为TRUE
2. 初始状态下，listen输出为TRUE
3. 状态转换是原子性的，不会出现中间状态
4. 建议使用PLC验证工具对形式化属性进行验证，确保逻辑正确性

## 7. 版本历史

- v1.0.0: 初始版本，实现基本状态机逻辑