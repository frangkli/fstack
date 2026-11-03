import { expectTypeOf, it } from "vitest";

import { parsePort } from "./parse-port";

it("narrows to the port on a valid outcome", () => {
  const result = parsePort("80");
  if (result.outcome === "valid") {
    expectTypeOf(result.port).toEqualTypeOf<number>();
  }
  // @ts-expect-error -- an invalid outcome carries no port
  expectTypeOf(parsePort("x").port).toBeNumber();
});
