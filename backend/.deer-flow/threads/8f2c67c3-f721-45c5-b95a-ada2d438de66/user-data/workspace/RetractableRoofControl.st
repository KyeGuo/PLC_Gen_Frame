FUNCTION_BLOCK RetractableRoofControl
VAR_INPUT
    RainSensor : BOOL; (* Input to detect rain *)
    WindSensor : BOOL; (* Input to detect wind *)
    TemperatureSensor : REAL; (* Input to measure temperature *)
END_VAR
VAR_OUTPUT
    RoofMotor : BOOL; (* Output to control the roof motor *)
END_VAR
VAR
    (* Internal state variables *)
END_VAR

// Retractable Roof Control - Main Logic
// Based on rain, wind, and temperature inputs to control roof motor

(*
Control Logic Rules:
1. Rain + Wind → RoofMotor=FALSE (完全关闭)
2. Rain only → RoofMotor=TRUE (部分关闭)
3. No Rain + Temp <20°C → RoofMotor=TRUE (轻微关闭)
4. No Rain + Temp ≥20°C → RoofMotor=FALSE (完全打开)
*)

// State machine implementation
CASE TRUE OF
    // Rule 1: Rain and Wind detected - Fully close roof
    RainSensor AND WindSensor:
        RoofMotor := FALSE;
    // Rule 2: Rain detected but no wind - Partially close roof
    RainSensor AND NOT WindSensor:
        RoofMotor := TRUE;
    // Rule 3: No rain and temperature below 20°C - Slightly close roof
    NOT RainSensor AND (TemperatureSensor < 20.0):
        RoofMotor := TRUE;
    // Rule 4: No rain and temperature 20°C or above - Fully open roof
    NOT RainSensor AND (TemperatureSensor >= 20.0):
        RoofMotor := FALSE;
    // Default case should theoretically never be reached
    ELSE:
        RoofMotor := FALSE; // Safety fallback: close roof if unexpected state
END_CASE;