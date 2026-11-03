import { describe, expect, it } from "vitest";

import { parsePort } from "./parse-port";

describe("parsePort", () => {
  it("reads a port in range", () => {
    expect(parsePort("8080")).toEqual({ outcome: "valid", port: 8080 });
  });

  it("rejects blank text instead of reading it as port 0", () => {
    expect(parsePort("")).toEqual({ outcome: "invalid", reason: "not-a-number" });
    expect(parsePort(" ")).toEqual({ outcome: "invalid", reason: "not-a-number" });
  });

  it("rejects a port past 65535", () => {
    expect(parsePort("70000")).toEqual({ outcome: "invalid", reason: "out-of-range" });
  });
});
