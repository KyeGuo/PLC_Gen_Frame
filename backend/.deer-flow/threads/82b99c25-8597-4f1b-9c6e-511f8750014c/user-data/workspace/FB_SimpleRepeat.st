FUNCTION_BLOCK FB_SimpleRepeat
VAR_INPUT
    INPUT_VAR1 : INT := 2;    // 初始值为2的输入变量
    INPUT_COUNTER : INT := 4; // 初始值为4的计数器输入
END_VAR
VAR_OUTPUT
    OUTPUT_VAR1 : INT;        // 输出变量
END_VAR
VAR
    COUNTER : INT;            // 内部计数器变量
END_VAR

// 初始化输出变量和内部计数器
OUTPUT_VAR1 := INPUT_VAR1;
COUNTER := INPUT_COUNTER;

// REPEAT循环实现重复乘法逻辑
REPEAT
    OUTPUT_VAR1 := OUTPUT_VAR1 * 2;  // 每次将输出乘以2
    COUNTER := COUNTER - 1;          // 计数器减1
UNTIL COUNTER = 0                    // 直到计数器等于0
END_REPEAT;