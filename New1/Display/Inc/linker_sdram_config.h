/**
 * @file linker_sdram_config.h
 * @brief STM32H7 SDRAM Linker Script Configuration Guide
 * 
 * This file explains how to configure the linker script for framebuffer placement
 * in SDRAM, which is required for the UI rendering system.
 */

/*
================================================================================
LINKER SCRIPT MODIFICATIONS FOR STM32H7 SDRAM FRAMEBUFFER
================================================================================

The UI rendering system uses a framebuffer placed in SDRAM for efficient rendering.
Follow these steps to properly configure your linker script:

1. MEMORY SECTION MODIFICATION
================================
Add/modify the MEMORY section in your .ld file:

MEMORY
{
    DTCMRAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 128K
    RAM (xrw)       : ORIGIN = 0x20020000, LENGTH = 384K
    ITCMRAM (xrw)   : ORIGIN = 0x00000000, LENGTH = 64K
    FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 2048K
    SDRAM (xrw)     : ORIGIN = 0xC0000000, LENGTH = 32M    /* FMC SDRAM */
}

2. SECTIONS MODIFICATION
=========================
Add the following section to place framebuffer in SDRAM:

/* SDRAM section for framebuffer */
.sdram (NOLOAD) :
{
    . = ALIGN(4);
    _sdram_start = .;
    *(SORT(.sdram*))
    . = ALIGN(4);
    _sdram_end = .;
} > SDRAM AT > SDRAM

Place this section BEFORE the closing brace of SECTIONS { ... }

3. INITIALIZATION CODE
=======================
Ensure your startup code initializes SDRAM before using the framebuffer:

In SystemInit() or similar startup function, initialize the FMC SDRAM controller:
- Configure GPIO for SDRAM signals
- Configure FMC memory interface
- Configure SDRAM timing parameters
- Send initialization commands to SDRAM

This is typically done by STMCubeMX-generated code in the system setup.

4. FRAMEBUFFER PLACEMENT
=========================
With the linker script configured, declare framebuffer as:

__attribute__((section(".sdram")))
uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

The linker will automatically place this in SDRAM.

5. CACHE CONSIDERATIONS
========================
For STM32H7 with data cache, consider:

- Disable caching for SDRAM region (if using hardware cache)
- Or properly manage cache coherency when updating framebuffer
- Use __DSB() and __ISB() barriers when needed

Example cache disable:
    SCB->DACR = 0;  // Disable data cache completely
    Or use MPU to disable caching for SDRAM region only

================================================================================
*/

/* Memory layout for reference:
     0x00000000 - 0x0000FFFF  : ITCM-RAM (64 KB)   - Code cache
     0x20000000 - 0x2001FFFF  : DTCM-RAM (128 KB)  - Data cache
     0x20020000 - 0x2007FFFF  : RAM (384 KB)       - Main RAM
     0x08000000 onward        : Flash              - Program storage
     0x24000000 - 0x2404FFFF  : AXI SRAM (320 KB)  - Framebuffer location
   
     Current framebuffer: 0x24000000 (AXI SRAM D1 domain)
     Size for 480x272 RGB565: 480 * 272 * 2 = 261 KB (fits in 320KB)
*/
