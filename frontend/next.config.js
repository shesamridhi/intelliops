/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone", // smaller, self-contained Docker image
};

module.exports = nextConfig;
