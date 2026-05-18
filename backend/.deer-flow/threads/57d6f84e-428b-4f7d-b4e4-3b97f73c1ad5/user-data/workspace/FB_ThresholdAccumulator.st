FUNCTION_BLOCK FB_ThresholdAccumulator
VAR_INPUT
    i : DINT;
END_VAR
VAR_OUTPUT
    o : DINT;
END_VAR
VAR
    s1 : DINT;
END_VAR

METHOD FB_INIT
VAR_INPUT
    bInitRetains : BOOL;
    bInCopyCode : BOOL;
END_VAR
// 初始化方法，根据TwinCAT规范必须实现
END_METHOD

METHOD MAIN
VAR
    s1_temp : DINT;
END_VAR
// 1. 每次调用功能块时初始化s1为0
    s1_temp := 0;
    
// 2. 如果输入i大于0，将其值添加到s1
    IF i > 0 THEN
        s1_temp := s1_temp + i;
    END_IF
    
// 3. 在第一个条件之后，如果s1等于42，添加8000到s1
    IF s1_temp = 42 THEN
        s1_temp := s1_temp + 8000;
    END_IF
    
// 4. 最终输出
    IF s1_temp < 0 THEN
        o := 0;
    ELSE
        // 确保输出不超过DINT最大值
        IF s1_temp > DINT#2147483647 THEN
            o := DINT#2147483647;
        ELSE
            o := s1_temp;
        END_IF
    END_IF
    
// 更新内部变量s1
    s1 := o;
END_METHOD
END_FUNCTION_BLOCK