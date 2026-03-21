#!/bin/bash
# Weekly Capability Evolver Agent Run
# Runs every Sunday at 3:00 AM

cd /home/admin/.openclaw/workspace

# Log the execution
echo "$(date): Running weekly capability-evolver agent evolution" >> /home/admin/.openclaw/workspace/logs/capability-evolver.log 2>&1

# Execute the capability-evolver skill
# This will be called by OpenClaw when the cron job triggers