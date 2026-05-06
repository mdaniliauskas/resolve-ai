import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output bundles everything needed to run in a Docker container
  // without node_modules — required for Cloud Run deployment
  output: "standalone",
};

export default nextConfig;
