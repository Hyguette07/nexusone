/** Project WGS84 onto the Kigali schematic (no map vendor key). */

export const KIGALI_BOUNDS = {
  latMin: -2.02,
  latMax: -1.90,
  lonMin: 30.02,
  lonMax: 30.16,
};

export type MapPoint = { x: number; y: number };

export function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

export function projectKigali(lat: number, lon: number): MapPoint {
  const { latMin, latMax, lonMin, lonMax } = KIGALI_BOUNDS;
  const x = ((lon - lonMin) / (lonMax - lonMin)) * 100;
  const y = ((latMax - lat) / (latMax - latMin)) * 100;
  return { x: clamp(x, 2, 98), y: clamp(y, 2, 98) };
}

export const DISTRICTS = [
  { name: "Nyabugogo", lat: -1.94, lon: 30.044 },
  { name: "Nyarugenge", lat: -1.944, lon: 30.061 },
  { name: "Kacyiru", lat: -1.944, lon: 30.078 },
  { name: "Remera", lat: -1.958, lon: 30.112 },
  { name: "Kimironko", lat: -1.949, lon: 30.125 },
  { name: "Nyamirambo", lat: -1.98, lon: 30.04 },
  { name: "Gikondo", lat: -1.975, lon: 30.075 },
  { name: "Kicukiro", lat: -1.978, lon: 30.1 },
  { name: "Kanombe", lat: -1.968, lon: 30.135 },
];
