# StateMachineControl 功能块设计文档

## 1. 概述
StateMachineControl是一个双状态PLC功能块，用于实现Idle和Processing两个状态的切换控制，满足特定的输入输出和状态转换规则。

## 2. 接口定义

### 输入变量
| 变量名   | 类型   | 描述                     |
|----------|--------|--------------------------|
| request  | BOOL   | 启动请求信号，上升沿有效 |
| done     | BOOL   | 完成信号，上升沿有效     |

### 输出变量
| 变量名  | 类型   | 描述                                             |
|---------|--------|--------------------------------------------------|
| listen  | BOOL   | 监听状态输出，仅在Idle状态为TRUE，Processing状态为FALSE |

### 内部变量
| 变量名 | 类型   | 描述                                  |
|--------|--------|---------------------------------------|
| state  | INT    | 状态存储变量，0=Idle(初始值)，1=Processing |

## 3. 状态转换逻辑

### Idle状态 (state=0)
- 当`request`为TRUE时，转换到Processing状态(state=1)
- 输出`listen`为TRUE

### Processing状态 (state=1)
- 当`done`为TRUE时，转换回Idle状态(state=0)
- 输出`listen`为FALSE

### 异常处理
- 如果state为非0非1的异常值，强制回到Idle状态(state=0)并设置listen为TRUE

## 4. 形式化属性验证

本功能块设计满足以下形式化属性：

1. **状态完整性**：state只能是0或1
2. **listen输出正确性**：listen为TRUE当且仅当state=0
3. **Idle到Processing转换**：当state=0且request=TRUE时，state将变为1
4. **Processing到Idle转换**：当state=1且done=TRUE时，state将变为0
5. **Processing状态保持**：当state=1且done=FALSE时，state保持为1
6. **状态不变式**：state始终为0或1

## 5. 使用示例

```iecst
VAR
    smc : StateMachineControl;
    startRequest : BOOL;
    processDone : BOOL;
    systemListening : BOOL;
END_VAR

// 调用功能块
smc(request := startRequest, done := processDone, listen => systemListening);
```

## 6. 测试建议

### 测试用例1：Idle状态到Processing状态转换
- 初始状态：state=0, listen=TRUE
- 输入：request=TRUE, done=FALSE
- 期望结果：state=1, listen=FALSE

### 测试用例2：Processing状态到Idle状态转换
- 初始状态：state=1, listen=FALSE
- 输入：request=FALSE, done=TRUE
- 期望结果：state=0, listen=TRUE

### 测试用例3：Processing状态保持
- 初始状态：state=1, listen=FALSE
- 输入：request=FALSE, done=FALSE
- 期望结果：state=1, listen=FALSE

### 测试用例4：异常状态处理
- 初始状态：state=2, listen=TRUE
- 输入：request=FALSE, done=FALSE
- 期望结果：state=0, listen=TRUE

### 测试用例5：同时触发request和done
- 初始状态：state=0, listen=TRUE
- 输入：request=TRUE, done=TRUE
- 期望结果：state=1, listen=FALSE (Idle到Processing转换优先于Processing到Idle转换)