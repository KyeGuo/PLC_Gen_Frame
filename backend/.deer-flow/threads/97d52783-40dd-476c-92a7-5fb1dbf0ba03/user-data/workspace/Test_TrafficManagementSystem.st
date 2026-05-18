PROGRAM Test_TrafficManagementSystem
VAR
    fbTMS : TrafficManagementSystem;
    
    (* 测试用例 *)
    TestCase : INT := 0;
    Result : BOOL := TRUE;
    
    (* 输入变量 *)
    VehicleCount1 : INT;
    VehicleCount2 : INT;
    VehicleCount3 : INT;
    VehicleCount4 : INT;
    
    (* 预期输出 *)
    ExpectedTL1 : BOOL;
    ExpectedTL2 : BOOL;
    ExpectedTL3 : BOOL;
    ExpectedTL4 : BOOL;
END_VAR

CASE TestCase OF
    0: (* 初始化 *)
        TestCase := 1;
        
    1: (* 测试用例1: VehicleCount1 > VehicleCount2 (正数值) *)
        VehicleCount1 := 10;
        VehicleCount2 := 5;
        VehicleCount3 := 3;
        VehicleCount4 := 8;
        
        ExpectedTL1 := TRUE;
        ExpectedTL2 := FALSE;
        ExpectedTL3 := FALSE;
        ExpectedTL4 := TRUE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 2;
        END_IF
        
    2: (* 测试用例2: VehicleCount2 > VehicleCount1 (正数值) *)
        VehicleCount1 := 5;
        VehicleCount2 := 10;
        VehicleCount3 := 8;
        VehicleCount4 := 3;
        
        ExpectedTL1 := FALSE;
        ExpectedTL2 := TRUE;
        ExpectedTL3 := TRUE;
        ExpectedTL4 := FALSE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 3;
        END_IF
        
    3: (* 测试用例3: VehicleCount1 = VehicleCount2 *)
        VehicleCount1 := 7;
        VehicleCount2 := 7;
        VehicleCount3 := 7;
        VehicleCount4 := 7;
        
        ExpectedTL1 := FALSE;
        ExpectedTL2 := TRUE;
        ExpectedTL3 := FALSE;
        ExpectedTL4 := TRUE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 4;
        END_IF
        
    4: (* 测试用例4: 负数输入处理 *)
        VehicleCount1 := -5;
        VehicleCount2 := 3;
        VehicleCount3 := -2;
        VehicleCount4 := -4;
        
        ExpectedTL1 := FALSE; // -5 -> 0, 0 < 3
        ExpectedTL2 := TRUE;
        ExpectedTL3 := TRUE;  // -2 -> 0, -4 -> 0, 0 不大于 0，所以应该是FALSE？
        ExpectedTL4 := FALSE; // 这里需要注意：0 > 0 为FALSE，所以TrafficLight3=FALSE, TrafficLight4=TRUE
        // 修正预期值
        ExpectedTL3 := FALSE;
        ExpectedTL4 := TRUE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 5;
        END_IF
        
    5: (* 测试用例5: 所有输入为0 *)
        VehicleCount1 := 0;
        VehicleCount2 := 0;
        VehicleCount3 := 0;
        VehicleCount4 := 0;
        
        ExpectedTL1 := FALSE;
        ExpectedTL2 := TRUE;
        ExpectedTL3 := FALSE;
        ExpectedTL4 := TRUE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 6;
        END_IF
        
    6: (* 测试用例6: 混合正负值 *)
        VehicleCount1 := -10;
        VehicleCount2 := -5;
        VehicleCount3 := 15;
        VehicleCount4 := -3;
        
        ExpectedTL1 := FALSE; // -10->0, -5->0, 0不大于0
        ExpectedTL2 := TRUE;
        ExpectedTL3 := TRUE;  // 15 > (-3->0)
        ExpectedTL4 := FALSE;
        
        fbTMS(VehicleCount1:=VehicleCount1, VehicleCount2:=VehicleCount2, 
             VehicleCount3:=VehicleCount3, VehicleCount4:=VehicleCount4);
        
        Result := (fbTMS.TrafficLight1 = ExpectedTL1) AND 
                  (fbTMS.TrafficLight2 = ExpectedTL2) AND
                  (fbTMS.TrafficLight3 = ExpectedTL3) AND
                  (fbTMS.TrafficLight4 = ExpectedTL4);
        
        IF NOT Result THEN
            TestCase := 99; // 测试失败
        ELSE
            TestCase := 100; // 所有测试通过
        END_IF
        
    100: (* 所有测试通过 *)
        Result := TRUE;
        
    99: (* 测试失败 *)
        Result := FALSE;
        
END_CASE
END_PROGRAM