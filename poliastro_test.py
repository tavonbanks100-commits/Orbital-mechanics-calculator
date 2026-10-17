
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
import astropy.units as u
import numpy as np
import csv

EARTH_RADIUS_KM = 6371.0
GRAVITATIONAL_PARAMETER = 398600.4418  # km^3/s^2 for Earth

def compute_orbits(alt_km, ecc=0.0):
    a = (EARTH_RADIUS_KM + alt_km) * u.km

    if ecc == 0.0:
        orbit = Orbit.circular(Earth, alt_km * u.km)
    else:
        orbit = Orbit.from_classical(Earth, a, ecc * u.one, 0*u.deg, 0*u.deg, 0*u.deg, 0*u.deg)

    velocity_mag = np.linalg.norm(orbit.v.to_value(u.km / u.s))
    radius_km = np.linalg.norm(orbit.r.to_value(u.km))
    manual_velocity = np.sqrt(GRAVITATIONAL_PARAMETER * (2/radius_km - 1/a.to_value(u.km)))
    period_min = orbit.period.to(u.min).value

    return velocity_mag, manual_velocity, period_min
    

def get_altitudes():
    raw = input("Enter altitude km and optional ecc (e.g. '400' or '400, 378028 0.0549'): ")
    orbits=[]
    for entry in raw.split(","):
        parts = entry.strip().split()
        if not parts:
            continue
        alt_km = float(parts[0])
        ecc = float(parts[1]) if len(parts) > 1 else 0.0
        orbits.append((alt_km, ecc))
    if not orbits:
        print("No valid values entered; using the default altitude of 400 km circular.")
        return [(400.0, 0.0)]
    return orbits
    
results = []
for alt_km, ecc in get_altitudes():
    velocity_mag, manual_velocity_kms, period_min = compute_orbits(alt_km, ecc)
    velocity_mph = velocity_mag * 2236.94
    manual_velocity_mph = manual_velocity_kms * 2236.94

    results.append({
        "alt_km": alt_km,
        "ecc": ecc,
        "velocity_mag": velocity_mag,
        "manual_velocity_kms": manual_velocity_kms,
        "velocity_mph": velocity_mph,
        "manual_velocity_mph": manual_velocity_mph,
        "period_min": period_min,
        "period_days": period_min / 1440
    })
    
    print(f"At {alt_km:.1f} km altitude with eccentricity {ecc:.4f}:")
    print(f"poliastro velocity: {velocity_mag:.2f} km/s, {velocity_mph:.2f} mph")
    print(f"manual velocity: {manual_velocity_kms:.2f} km/s, {manual_velocity_mph:.2f} mph")
    print(f"period: {period_min/60:.2f} hours, {period_min/1440:.2f} days")
    print()

with open("orbit.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"saved {len(results)} orbits to orbit.csv")
    
