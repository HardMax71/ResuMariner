declare module 'plantuml-encoder' {
  export function encode(puml: string): string;
  export function decode(encoded: string): string;
  export default { encode, decode };
}
