import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  allowedDevOrigins: ["*.friend.kskshome.xyz"],
};

export default nextConfig;
