#!/usr/bin/env bash
echo "Deploying..."
sleep 1
echo "Getting Ready..."
origin_dir=$(pwd)
cd ..
rsync -avz --del $origin_dir pi@10.0.1.7:/opt/mycroft/skills/communications-skill/
echo "Done!"
exit 0
