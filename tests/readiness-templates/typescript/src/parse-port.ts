/** A TCP port read from text: an integer from 1 to 65535, or why the text isn't one. */
export type PortParse =
  | { readonly outcome: "valid"; readonly port: number }
  | { readonly outcome: "invalid"; readonly reason: "not-a-number" | "out-of-range" };

/** Parses a port from untrusted text, such as an environment variable. */
export function parsePort(text: string): PortParse {
  // Number("") and Number(" ") are 0, so the digits are checked before converting.
  if (!/^\d+$/.test(text)) {
    return { outcome: "invalid", reason: "not-a-number" };
  }
  const port = Number(text);
  if (port < 1 || port > 65_535) {
    return { outcome: "invalid", reason: "out-of-range" };
  }
  return { outcome: "valid", port };
}
