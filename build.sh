#!/bin/bash
set -e

echo "🔨 Building frontend with Vite..."
cd webapp
npm install
npm run build
cd ..

echo "✅ Frontend build complete!"
ls -la webapp_dist/