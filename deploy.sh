#!/usr/bin/env bash
echo "Deploying..."
sleep 1
echo "Getting Ready..."
skill_dir=$(pwd)
cd ..
scp -r $skill_dir pi@10.0.1.7:/opt/mycroft/skills/communications-skill
echo "Done!"
