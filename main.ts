// news-image-20261119 entry (Node 22, standard library only).
//
// The artwork ships in the repository as entry.png, beside this file; the
// grader mounts the repository at /bot and the program's whole job is to
// deliver those bytes, unchanged, to /output/entry.png. Before copying it
// verifies the file is really there, really a PNG and really within the
// competition's size cap, so a broken snapshot fails loudly at run time
// instead of quietly submitting nothing.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1_048_576; // the gate's 1 MiB cap
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const sourcePath = fileURLToPath(new URL('./entry.png', import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputPath = join(outputDir, 'entry.png');

let bytes: Buffer;
try {
  bytes = readFileSync(sourcePath);
} catch {
  throw new Error(`entry image not found next to main.ts at ${sourcePath}`);
}

const hasSignature =
  bytes.length >= PNG_SIGNATURE.length &&
  PNG_SIGNATURE.every((byte, i) => bytes[i] === byte);
if (!hasSignature) {
  throw new Error('entry.png does not start with the PNG signature');
}
if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES} cap`);
}

// The first chunk after the signature must be IHDR; its payload opens with
// the image's width and height as big-endian uint32s (file offsets 16..24).
// The gate refuses anything past 1024 in either dimension, so check here.
const MAX_DIMENSION = 1024;
if (bytes.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk where the header requires one');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
  throw new Error(`entry.png is ${width}x${height}, over the ${MAX_DIMENSION}px cap`);
}

mkdirSync(outputDir, { recursive: true });
writeFileSync(outputPath, bytes);
console.log(`wrote ${outputPath} (${bytes.length} bytes, ${width}x${height})`);
