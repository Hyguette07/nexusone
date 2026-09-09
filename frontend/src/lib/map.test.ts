import { describe, expect, it } from "vitest";
import { clamp, projectKigali } from "./map";

describe("projectKigali", () => {
  it("puts the city centre near the middle of the schematic", () => {
    const p = projectKigali(-1.95, 30.06);
    expect(p.x).toBeGreaterThan(20);
    expect(p.x).toBeLessThan(50);
    expect(p.y).toBeGreaterThan(30);
    expect(p.y).toBeLessThan(70);
  });

  it("places Kimironko east of Nyabugogo", () => {
    const west = projectKigali(-1.94, 30.044);
    const east = projectKigali(-1.949, 30.125);
    expect(east.x).toBeGreaterThan(west.x);
  });

  it("clamps out-of-city points onto the board", () => {
    const p = projectKigali(0, 0);
    expect(p.x).toBe(2);
    expect(p.y).toBe(2);
  });
});

describe("clamp", () => {
  it("bounds a number", () => {
    expect(clamp(5, 0, 3)).toBe(3);
    expect(clamp(-1, 0, 3)).toBe(0);
  });
});
