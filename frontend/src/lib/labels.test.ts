import { describe, expect, it } from "vitest";
import { scoreBand, TYPE_LABEL } from "./labels";

describe("scoreBand", () => {
  it("labels DispatchRanker bands", () => {
    expect(scoreBand(91)).toBe("Prime pick");
    expect(scoreBand(66)).toBe("Strong");
    expect(scoreBand(44)).toBe("Usable");
    expect(scoreBand(12)).toBe("Last resort");
  });
});

describe("TYPE_LABEL", () => {
  it("covers every incident domain", () => {
    expect(TYPE_LABEL.FLOOD).toBe("Flood");
    expect(TYPE_LABEL.MISSING_PERSON).toBe("Missing person");
  });
});
