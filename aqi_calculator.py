"""
EPA AQI Calculator

Implements the official US EPA formula for converting raw pollutant
concentrations into a standardized AQI value (0-500 scale).

This becomes our TARGET variable for model training, replacing
raw PM2.5 - matching mentor guidance to predict AQI directly.

Reference: US EPA technical documentation for the National AQI.
"""

# ---------------------------------------------------------------
# BREAKPOINT TABLES
# Each entry: (concentration_low, concentration_high, aqi_low, aqi_high)
# These are official EPA-defined breakpoints.
# ---------------------------------------------------------------

PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 350.4, 301, 400),
    (350.5, 500.4, 401, 500),
]

PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 504, 301, 400),
    (505, 604, 401, 500),
]

# CO is measured in ppm in the official standard, but our API gives
# it in µg/m3. We convert using the standard factor for CO: 1 ppm ≈ 1145 µg/m3
CO_BREAKPOINTS = [
    (0.0, 4.4, 0, 50),
    (4.5, 9.4, 51, 100),
    (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200),
    (15.5, 30.4, 201, 300),
    (30.5, 40.4, 301, 400),
    (40.5, 50.4, 401, 500),
]

# O3 (ozone) - 8-hour average, in ppb. Our API gives µg/m3.
# Conversion factor for O3: 1 ppb ≈ 1.96 µg/m3 (approx, at standard conditions)
O3_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 70, 51, 100),
    (71, 85, 101, 150),
    (86, 105, 151, 200),
    (106, 200, 201, 300),
]


def calculate_sub_index(concentration: float, breakpoints: list) -> float:
    """
    Given a raw concentration and the appropriate breakpoint table,
    finds which bracket it falls into and calculates the AQI sub-index
    using EPA's official linear interpolation formula:

        I = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low

    Where:
        I = the AQI sub-index we're calculating
        C = the actual pollutant concentration
        C_low, C_high = the concentration bracket bounds
        I_low, I_high = the corresponding AQI bracket bounds
    """
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            return round(aqi)

    # If concentration exceeds all defined brackets, cap at 500 (max AQI)
    return 500


def calculate_aqi(pm25: float, pm10: float, co: float, o3: float) -> int:
    """
    Calculates the overall AQI by computing a sub-index for each
    pollutant, then returning the HIGHEST one - this is the EPA's
    'dominant pollutant' rule: your overall AQI is only as good as
    your worst pollutant.
    """
    # Convert units where needed
    co_ppm = co / 1145        # µg/m3 -> ppm
    o3_ppb = o3 / 1.96         # µg/m3 -> ppb

    sub_indices = {
        "pm25": calculate_sub_index(pm25, PM25_BREAKPOINTS),
        "pm10": calculate_sub_index(pm10, PM10_BREAKPOINTS),
        "co": calculate_sub_index(co_ppm, CO_BREAKPOINTS),
        "o3": calculate_sub_index(o3_ppb, O3_BREAKPOINTS),
    }

    overall_aqi = max(sub_indices.values())
    return overall_aqi


# ---- Quick test when running this file directly ----
if __name__ == "__main__":
    # Test using your actual Ghotki reading from earlier:
    # pm2_5: 34.72, pm10: 113.19, co: 180.07, o3: 69.22
    test_aqi = calculate_aqi(pm25=34.72, pm10=113.19, co=180.07, o3=69.22)
    print(f"Calculated AQI: {test_aqi}")