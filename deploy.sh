#!/usr/bin/env bash
echo "Deploying..."
sleep 1
echo "Getting Ready..."
skill_dir=$(pwd)
cd ..
rsync -avz --del $skill_dir pi@10.0.1.7:/opt/mycroft/skills/
echo "Done!"
