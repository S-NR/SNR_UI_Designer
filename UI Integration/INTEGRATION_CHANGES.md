# Display UI Integration Changes

**Date:** February 27, 2026  
**Project:** STM32H735 UI Integration  
**Purpose:** Integration of Display folder UI rendering code with STM32H735 buildable firmware

---

## Overview

This document details all modifications made to integrate the custom UI rendering system (Display folder) with the STM32H735IGKx project, enabling UI rendering on an 800x480 display with LTDC hardware acceleration.

---

## 1. Linker Script Modifications

### File: `STM32H735IGKX_FLASH.ld`

#### Changes:
1. **Added SDRAM Memory Region**
   - Location: Memory configuration section
   - Added: `SDRAM (xrw) : ORIGIN = 0xC0000000, LENGTH = 8M`
   - Purpose: Define external SDRAM memory space for framebuffers

2. **Added .sdram Section**
   - Location: After `._user_heap_stack` section
   - Added section definition:
     ```ld
     .sdram (NOLOAD) :
     {
       . = ALIGN(4);
       *(.sdram)
       *(.sdram*)
       . = ALIGN(4);
     } >SDRAM
     ```
   - Purpose: Place framebuffer variables in SDRAM without loading from flash

---

## 2. Build System Updates

### File: `Debug/sources.mk`

#### Changes:
- Added `Display/Src \` to SUBDIRS list
- Purpose: Include Display source files in build process

### File: `Debug/Display/Src/subdir.mk` (NEW FILE)

#### Purpose:
Complete makefile rules for building Display folder source files

#### Contents:
- Source files: `generated_ui.c`, `ui_layout.c`, `ui_renderer.c`, `ui_stm_integration.c`
- Compiler flags: Added `-DSTM32H7_DMA2D_ENABLE` and `-I../Display/Inc`
- Build rules for object files, dependencies, and cyclomatic complexity analysis

### File: `Debug/Core/Src/subdir.mk`

#### Changes:
- Added `fmc.c` to C_SRCS, OBJS, and C_DEPS
- Purpose: Include FMC/SDRAM driver in build

---

## 3. FMC/SDRAM Driver (NEW)

### File: `Core/Inc/fmc.h` (NEW FILE)

#### Purpose:
Header file for FMC SDRAM peripheral driver

#### Contents:
- Function prototype: `void MX_FMC_Init(void)`
- External handle: `SDRAM_HandleTypeDef hsdram1`

### File: `Core/Src/fmc.c` (NEW FILE)

#### Purpose:
Initialize external SDRAM for framebuffer storage

#### Key Configurations:

**SDRAM Parameters:**
- Bank: FMC_SDRAM_BANK1
- Column bits: 8
- Row bits: 12
- Data width: 16-bit
- Internal banks: 4
- CAS latency: 3 cycles
- Clock period: 2 (HCLK/2)
- Base address: 0xC0000000

**Timing Parameters:**
- Load to Active Delay: 2
- Exit Self Refresh Delay: 7
- Self Refresh Time: 4
- Row Cycle Delay: 7
- Write Recovery Time: 3
- RP Delay: 2
- RCD Delay: 2

**Initialization Sequence:**
1. Clock enable command
2. 100μs delay
3. Precharge all command
4. Auto-refresh command (8 cycles)
5. Mode register programming
6. Refresh rate counter: 1542 (for 64ms/4096 rows @ 100MHz)

**GPIO Pins Configured:**
- GPIOF: A0-A9 (address lines)
- GPIOG: A10-A12, BA0-BA1, SDCLK, SDNCAS
- GPIOE: D4-D7, NBL0-NBL1
- GPIOD: D0-D3, D13-D15
- GPIOC: SDCKE0, SDNWE

---

## 4. LTDC Display Configuration

### File: `Core/Src/ltdc.c`

#### Changes:
Modified Layer 0 configuration in `LTDC_Init 2` user code section:

**Parameters:**
- Window dimensions: 800x480 pixels
- Pixel format: `LTDC_PIXEL_FORMAT_RGB565` (16-bit color)
- Alpha: 255 (fully opaque)
- Blending: `PAxCA` mode
- Framebuffer address: `0xC0000000` (SDRAM base)
- Image size: 800x480

**Purpose:**
Configure LTDC layer to output UI from SDRAM framebuffer to display

---

## 5. Main Application Integration

### File: `Core/Src/main.c`

#### Changes:

**1. Added Includes:**
```c
#include "fmc.h"                  // SDRAM driver
#include "ui_stm_integration.h"   // Display low-level functions
#include "ui_renderer.h"          // UI rendering engine
#include "generated_ui.h"         // UI object definitions
```

**2. Added Peripheral Initialization:**
- Added `MX_FMC_Init();` call before LTDC initialization
- Purpose: Initialize SDRAM before LTDC attempts to use it

**3. Added UI Initialization (USER CODE BEGIN 2):**
```c
/* Initialize UI Display System */
UI_RenderInit();
```
- Purpose: Clear framebuffer and initialize rendering system

**4. Added Rendering Loop (USER CODE BEGIN 3):**
```c
/* Render UI at ~60 FPS */
UI_Render();
HAL_Delay(16);  /* Approximately 60 FPS (16ms delay) */
```
- Purpose: Continuously render UI objects to framebuffer

---

## 6. Display Folder Structure

### Files Integrated:

#### `Display/Inc/`
- `generated_ui.h` - UI object type definitions
- `ui_renderer.h` - Rendering backend configuration
- `ui_stm_integration.h` - STM32 hardware abstraction layer
- `linker_sdram_config.h` - SDRAM configuration reference

#### `Display/Src/`
- `generated_ui.c` - UI object array (rectangle + text)
- `ui_layout.c` - Layout calculations
- `ui_renderer.c` - Main rendering engine
- `ui_stm_integration.c` - Hardware-specific implementations

---

## 7. UI Content

### Current UI Objects (generated_ui.c):

1. **Rectangle**
   - Position: (211, 136)
   - Size: 100x50 pixels
   - Fill color: 0x867D (RGB565 gray)
   - Outline color: 0x0000 (black)

2. **Text**
   - Position: (258, 158)
   - Text: "Sample Text"
   - Color: 0x0000 (black)
   - Font size: 12

---

## 8. Hardware Acceleration Features

### DMA2D Support:
- Enabled via `STM32H7_DMA2D_ENABLE` compiler flag
- Used for fast rectangle fills
- Reduces CPU load during rendering

### Features:
- RGB565 pixel format (2 bytes per pixel)
- Double-buffering support (Layer 0 & Layer 1)
- Hardware-accelerated filled rectangles
- Software ellipse/oval rendering
- Basic text rendering

---

## 9. Memory Layout

### Flash Memory:
- Application code: 0x08000000
- Size: 1024 KB

### Internal RAM:
- ITCM: 64 KB @ 0x00000000
- DTCM: 128 KB @ 0x20000000
- AXI SRAM (D1): 320 KB @ 0x24000000
- AHB SRAM (D2): 32 KB @ 0x30000000
- AHB SRAM (D3): 16 KB @ 0x38000000

### External SDRAM:
- Base: 0xC0000000
- Size: 8 MB
- Framebuffer Layer 0: 0xC0000000 (768,000 bytes for 800x480x2)
- Framebuffer Layer 1: 0xC0180000 (offset for double-buffering)

---

## 10. Build Instructions

### Clean Build:
```bash
cd Debug
make clean
make all
```

### Expected Output:
- `UI Integration.elf` - Executable firmware
- `UI Integration.map` - Memory map
- `UI Integration.list` - Disassembly listing

---

## 11. Verification Checklist

### Hardware Prerequisites:
- [ ] STM32H735IGKx microcontroller
- [ ] External SDRAM chip (16-bit, 8MB minimum)
- [ ] LCD display (800x480 resolution)
- [ ] LTDC-compatible display interface

### Pin Verification Required:
- [ ] FMC pins match board schematic (see fmc.c GPIO configuration)
- [ ] LTDC pins match board schematic (auto-configured by CubeMX)
- [ ] SDRAM chip specifications match configuration

### Testing Steps:
1. Flash firmware to device
2. Power on - display should initialize
3. Verify UI renders (gray rectangle + "Sample Text")
4. Check for ~60 FPS rendering (smooth updates)

---

## 12. Configuration Dependencies

### Compiler Defines:
- `STM32H735xx` - Target MCU
- `STM32H7xx` - MCU family
- `STM32H7_DMA2D_ENABLE` - Hardware acceleration
- `USE_HAL_DRIVER` - STM32 HAL library

### Include Paths:
- `Core/Inc`
- `Display/Inc`
- `Drivers/STM32H7xx_HAL_Driver/Inc`
- `Drivers/CMSIS/Device/ST/STM32H7xx/Include`
- `Drivers/CMSIS/Include`

---

## 13. Performance Characteristics

### Frame Rate:
- Target: 60 FPS (16ms per frame)
- Actual: Depends on object count and DMA2D availability

### Memory Usage:
- Framebuffer size: 768,000 bytes (800 × 480 × 2)
- UI object array: 2 objects × ~64 bytes = 128 bytes
- Code size: ~10-15 KB (Display folder)

### CPU Load:
- With DMA2D: Low (hardware-accelerated fills)
- Without DMA2D: Moderate (software pixel writes)

---

## 14. Customization Points

### To Change Display Resolution:
1. Update `LTDC_WIDTH` and `LTDC_HEIGHT` in `Display/Inc/ui_stm_integration.h`
2. Update `LCD_WIDTH` and `LCD_HEIGHT` in `Display/Inc/ui_renderer.h`
3. Update LTDC timing in `Core/Src/ltdc.c`
4. Update layer window size in `Core/Src/ltdc.c`

### To Add New UI Objects:
1. Edit `Display/Src/generated_ui.c` - add objects to array
2. Update `UI_OBJECT_COUNT` in `Display/Inc/generated_ui.h`
3. Rebuild project

### To Change Frame Rate:
- Modify `HAL_Delay(16)` in main loop (16ms = 60 FPS, 33ms = 30 FPS)

---

## 15. Known Limitations

### Text Rendering:
- Basic placeholder implementation
- No font library integrated
- Limited to simple character blocks

### Touch Input:
- Not yet implemented
- Would require touch controller driver integration

### Advanced Graphics:
- No anti-aliasing
- No image/bitmap support
- No transparency blending (except via alpha channel)

---

## 16. Future Enhancements

### Recommended Additions:
1. Integrate font library (e.g., FreeType, or bitmap fonts)
2. Add touch controller support
3. Implement image/sprite rendering
4. Add animation framework
5. Optimize rendering (dirty rectangle tracking)
6. Add UI event handling system

---

## 17. Troubleshooting

### Display Shows Nothing:
- Check SDRAM initialization
- Verify FMC pins match hardware
- Check LTDC clock configuration
- Verify display power and timing

### Garbage/Corrupted Display:
- SDRAM timing may be incorrect
- Check refresh rate settings
- Verify pixel format matches display

### Build Errors:
- Ensure all Display files are in build system
- Check include paths in makefile
- Verify HAL drivers are configured

---

## Summary

All necessary integration work has been completed to render the UI from the Display folder on the STM32H735 hardware. The system is ready for compilation and testing on the target hardware, pending verification of hardware-specific pin configurations and SDRAM specifications.

**Total Files Modified:** 7  
**Total Files Created:** 4  
**Build System Files Updated:** 3

**Status:** ✅ Integration Complete - Ready for Hardware Testing
