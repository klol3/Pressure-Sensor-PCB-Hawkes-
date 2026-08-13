import time
import board
import analogio

sensor_pin = analogio.AnalogIn(board.A1)

MAX_ADC = 65535.0
VREF = 3.3
VS = 3.3  # Set to the actual supply voltage powering the MP3V5050 V_S pin

def read_voltage(pin, samples=20):
    """Averages multiple ADC samples to reduce reading noise."""
    total = sum(pin.value for _ in range(samples))
    avg_raw = total / samples
    return (avg_raw / MAX_ADC) * VREF

print("Calibrating zero-pressure baseline... Keep sensor unpressurized.")
time.sleep(1.0)

# Record resting voltage at 0 kPa
ZERO_OFFSET_VOLTAGE = read_voltage(sensor_pin, samples=50)
print(f"Zero Baseline Set: {ZERO_OFFSET_VOLTAGE:.3f} V")

def calculate_pressure(v_out, zero_voltage, v_s=3.3):
    """
    Calculates differential pressure using the MP3V5050 sensitivity slope (0.018 * Vs per kPa).
    """
    # Differential voltage above the rest state
    delta_v = v_out - zero_voltage
    if delta_v < 0:
        delta_v = 0.0
        
    # Sensitivity in V/kPa = 0.018 * Vs
    sensitivity = 0.018 * v_s
    
    p_kpa = delta_v / sensitivity
    p_psi = p_kpa * 0.145038
    return p_kpa, p_psi

print("\nStarting pressure measurement loop...")

while True:
    voltage = read_voltage(sensor_pin)
    p_kpa, p_psi = calculate_pressure(voltage, ZERO_OFFSET_VOLTAGE, v_s=VS)

    print(f"Voltage: {voltage:.3f} V | ΔV: {(voltage - ZERO_OFFSET_VOLTAGE):.3f} V | Pressure: {p_kpa:.2f} kPa ({p_psi:.2f} PSI)")
    time.sleep(0.1)
