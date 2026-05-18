# FB_MuseumClimateControl Interface Documentation

## Overview
The `FB_MuseumClimateControl` function block implements a complete climate control system for museums, managing temperature, humidity, and lighting based on sensor inputs.

## Input Variables

| Name | Type | Description |
|------|------|-------------|
| `HumiditySensor` | REAL | Current humidity reading from sensor (unit: %RH) |
| `TemperatureSensor` | REAL | Current temperature reading from sensor (unit: °C) |
| `LightSensor` | BOOL | Light presence detection (TRUE = ambient light detected) |
| `LightThreshold` | BOOL | Light control override (TRUE = enable automatic light control) |

## Output Variables

| Name | Type | Description |
|------|------|-------------|
| `HVACSystem` | BOOL | HVAC system control output (TRUE = ON, FALSE = OFF) |
| `Humidifier` | BOOL | Humidifier control output (TRUE = ON, FALSE = OFF) |
| `Dehumidifier` | BOOL | Dehumidifier control output (TRUE = ON, FALSE = OFF) |
| `LightControl` | BOOL | Lighting control output (TRUE = ON, FALSE = OFF) |

## Internal Variables

| Name | Type | Default Value | Description |
|------|------|---------------|-------------|
| `HumiditySetpoint` | REAL | 50.0 | Target humidity setpoint (unit: %RH) |
| `TemperatureSetpoint` | REAL | 20.0 | Target temperature setpoint (unit: °C) |

## Control Logic

### 1. Humidity Control
- Humidity < 50.0%: Activate Humidifier, Deactivate Dehumidifier
- Humidity > 50.0%: Activate Dehumidifier, Deactivate Humidifier
- Humidity = 50.0%: Deactivate both Humidifier and Dehumidifier

### 2. Temperature Control
- Temperature < 20.0°C OR > 20.0°C: Activate HVACSystem
- Temperature = 20.0°C: Deactivate HVACSystem

### 3. Lighting Control
- LightSensor = TRUE AND LightThreshold = TRUE: Deactivate LightControl (turn off lights)
- All other conditions: Activate LightControl (turn on lights)

### 4. Safety Interlock
- Redundant protection to ensure Humidifier and Dehumidifier never operate simultaneously
- If both would be active, the interlock automatically turns both off

## Usage Example
```st
VAR
    MuseumClimate : FB_MuseumClimateControl;
    Humidity : REAL;
    Temperature : REAL;
    LightDetected : BOOL;
    LightOverride : BOOL;
    HVAC : BOOL;
    Humidify : BOOL;
    Dehumidify : BOOL;
    Lights : BOOL;
END_VAR

// Call function block in cyclic program
MuseumClimate(
    HumiditySensor := Humidity,
    TemperatureSensor := Temperature,
    LightSensor := LightDetected,
    LightThreshold := LightOverride,
    HVACSystem => HVAC,
    Humidifier => Humidify,
    Dehumidifier => Dehumidify,
    LightControl => Lights
);
```

## Compliance
- IEC 61131-3 standard compliant
- TwinCAT 3 compatible
- Modular design for easy integration
- Safety interlocks for equipment protection
- Clear documentation and interface definitions