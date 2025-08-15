# Duckietown Ente Profile - Map Editor Fix

## Date: August 14, 2025
## Status: WORKING SOLUTION ✅

## Problem Summary
The `dts map editor` command in the ente profile was failing with:
1. `AttributeError: 'types.SimpleNamespace' object has no attribute 'start_gui_tools'`
2. Missing `dt_maps` module in Docker container
3. Import errors preventing GUI from launching

## Root Cause Analysis
1. **Missing start_gui_tools command**: The map editor tried to call `shell.include.start_gui_tools.command()` but this command doesn't exist in the ente profile
2. **Missing dt_maps module**: The Docker image `duckietown/dt-gui-tools:ente-amd64` doesn't have the `dt_maps` Python module installed
3. **Incomplete integration**: The ente profile is still under development and has incomplete command integration

## Solution Implemented

### File Modified
`/home/dan/.duckietown/shell/profiles/ente/commands/duckietown/map/editor/command.py`

### Key Changes
1. **Bypassed broken start_gui_tools**: Direct Docker container launch instead of using shell.include
2. **Added dt_maps workaround**: 
   - First tries to install `dt-maps` via pip
   - If that fails, creates a stub module with basic Map class
3. **Proper X11 forwarding**: Added xhost command and proper display environment variables
4. **Volume mounting**: Maps current directory to `/maps` in container for file persistence

### Technical Details
- **Docker Image**: `duckietown/dt-gui-tools:ente-amd64`
- **Launcher Script**: `/launch/dt-gui-tools/editor.sh` (inside container)
- **Map Editor Location**: `/code/src/dt-gui-tools/packages/map_editor/main.py` (inside container)

## How to Apply This Fix

### After Fresh Duckietown Installation:
```bash
# Copy the working command file
cp ~/working_map_editor_command.py /home/dan/.duckietown/shell/profiles/ente/commands/duckietown/map/editor/command.py

# Test the fix
dts map editor
```

## Current Status
- ✅ Map editor launches successfully
- ✅ GUI interface works (though "a bit janky")
- ⚠️ Save/load functionality needs testing
- ⚠️ Duckiematrix integration needs testing

## Next Steps for Proper Fix
1. **Root cause fix**: Implement proper `start_gui_tools` command in ente profile
2. **Docker image fix**: Add `dt_maps` module to `duckietown/dt-gui-tools:ente-amd64`
3. **Integration testing**: Verify save/load and Duckiematrix compatibility
4. **Submit PR**: Contribute fix back to Duckietown repositories

## Files to Backup Before Reinstallation
- `~/working_map_editor_command.py` (our working solution)
- This documentation file

## Repository Locations
- Shell commands: `/home/dan/duckietown-dev/duckietown-shell-commands/`
- GUI tools: `/home/dan/duckietown-dev/dt-gui-tools/`