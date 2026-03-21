---
name: capability-evolver
description: Automatically evolve and improve agent capabilities through self-reflection and skill enhancement
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"] }
      }
  }
---

# Capability Evolver Skill

This skill enables agents to automatically evolve their own capabilities through systematic self-improvement.

## Purpose

- Analyze current agent performance and identify improvement areas
- Generate new skills or enhance existing ones
- Update agent configuration and workspace files
- Perform weekly capability assessments and upgrades

## Usage

The capability-evolver runs comprehensive analysis of:
- Current skill set effectiveness
- Workspace organization and efficiency  
- Memory management and recall accuracy
- Tool usage patterns and optimization opportunities
- Security posture and risk assessment

## Configuration

Can be scheduled to run automatically via cron jobs for periodic self-improvement cycles.

## Output

Produces detailed reports on:
- Identified improvement opportunities
- New skill recommendations
- Configuration optimizations
- Performance benchmarks before/after changes

## Safety

- All changes are logged and reversible
- Critical system files are backed up before modification
- User approval required for major changes (unless configured for autonomous operation)