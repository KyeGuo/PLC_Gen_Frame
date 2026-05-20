iecst
FUNCTION_BLOCK SmartIrrigationSystem
VAR_INPUT
    SoilMoistureSensor1 : REAL;
    SoilMoistureSensor2 : REAL;
    WeatherForecast : INT; (* 0: Sunny, 1: Rainy, 2: Cloudy *)
END_VAR

VAR_OUTPUT
    WaterPump : BOOL;
END_VAR

VAR
    SoilMoistureThreshold : REAL := 30.0;
END_VAR

WaterPump := (WeatherForecast = 0) AND (SoilMoistureSensor1 < SoilMoistureThreshold OR SoilMoistureSensor2 < SoilMoistureThreshold);

END_FUNCTION_BLOCK