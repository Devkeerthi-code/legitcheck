import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath: basePath || undefined,
  assetPrefix: basePath || undefined,
  images: { unoptimized: true },
  poweredByHeader: false,
  reactStrictMode: true,
  // Pin the workspace root so a stray lockfile in a parent folder is never picked up.
  turbopack: { root: dirname(fileURLToPath(import.meta.url)) },
};

export default nextConfig;
