/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true, // Enables strict mode in React for better error handling
    swcMinify: true, // Enables faster minification with SWC
    images: {
        domains: [], // No external domains needed if all images are local
    },
  };
  
  module.exports = nextConfig;