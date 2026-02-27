# STM32H735G-DK Display Debugging Guide

## Problem Analysis

Your display isn't showing anything. Here are the issues found:

### 1. **LTDC Timing Configuration Mismatch**
**Issue**: `ltdc.c` lines 48-55 configure LTDC for ~640x480 resolution:
```c
hltdc.Init.AccumulatedActiveW = 654;  // 640 + porches
hltdc.Init.AccumulatedActiveH = 485;  // 480 + porches
```

But Layer 0 is configured for 480x272 window (lines 105-107).

**Problem**: LTDC controller timing must match the physical display resolution. STM32H735G-DK has an **800x480** RGB display.

### 2. **Missing LCD Power/Backlight Initialization**
**Issue**: STM32H735G-DK requires GPIO initialization for:
- LCD Backlight Enable (typically PL2 or check your board schematic)
- LCD Power Enable

Without these, the display stays off even if LTDC is sending data.

### 3. **DMA2D May Be Failing Silently**
The DMA2D hardware acceleration might not be properly initialized.

---

## Quick Test #1: Disable DMA2D (Software Rendering)

This tests if the issue is with DMA2D or the display itself.

### Step 1: Comment out DMA2D define
Edit `Display/Inc/ui_stm_integration.h` line 28:
```c
// #define STM32H7_DMA2D_ENABLE  // <-- Comment this out
```

### Step 2: Rebuild and test
- **Project** → **Build Project**
- Flash to board

**Expected**: If you see output now, DMA2D was the problem. If still blank, continue to Test #2.

---

## Quick Test #2: Enable LCD Backlight

### Add to `Core/Src/gpio.c` after `/* USER CODE BEGIN 2 */` (around line 204):

```c
/* USER CODE BEGIN 2 */

/* Enable LCD Backlight - STM32H735G-DK */
/* Note: Check your board schematic for correct backlight pin */
/* Common options: PL2, PK3, or check JP2 jumper position */

GPIO_InitTypeDef GPIO_InitStruct = {0};

/* Try PL2 first (common for STM32H735G-DK) */
__HAL_RCC_GPIOK_CLK_ENABLE();  // or GPIOK/GPIOL depending on pin

GPIO_InitStruct.Pin = GPIO_PIN_3;  // Adjust pin number based on your board
GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
GPIO_InitStruct.Pull = GPIO_NOPULL;
GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
HAL_GPIO_Init(GPIOK, &GPIO_InitStruct);  // Adjust port

/* Turn backlight ON */
HAL_GPIO_WritePin(GPIOK, GPIO_PIN_3, GPIO_PIN_SET);  // Adjust port/pin

/* USER CODE END 2 */
```

**Note**: You MUST check your board documentation for the correct backlight pin.

---

## Test #3: Fix LTDC Timing for STM32H735G-DK

The STM32H735G-DK has an **RK043FN48H-CT672B** display (800x480).

### Option A: Use Full 800x480 Resolution
Replace the LTDC_Init section in `Core/Src/ltdc.c` (lines 43-56):

```c
hltdc.Instance = LTDC;
hltdc.Init.HSPolarity = LTDC_HSPOLARITY_AL;
hltdc.Init.VSPolarity = LTDC_VSPOLARITY_AL;
hltdc.Init.DEPolarity = LTDC_DEPOLARITY_AL;
hltdc.Init.PCPolarity = LTDC_PCPOLARITY_IPC;
hltdc.Init.HorizontalSync = 40;  // HSYNC width
hltdc.Init.VerticalSync = 9;     // VSYNC height
hltdc.Init.AccumulatedHBP = 53;  // HSYNC + HBP
hltdc.Init.AccumulatedVBP = 11;  // VSYNC + VBP
hltdc.Init.AccumulatedActiveW = 853;  // HSYNC + HBP + Active = 53 + 800
hltdc.Init.AccumulatedActiveH = 491;  // VSYNC + VBP + Active = 11 + 480
hltdc.Init.TotalWidth = 865;     // Whole line (includes porches + sync)
hltdc.Init.TotalHeigh = 493;     // Whole frame
hltdc.Init.Backcolor.Blue = 0;
hltdc.Init.Backcolor.Green = 0;
hltdc.Init.Backcolor.Red = 0;
```

Then update Layer 0 configuration (lines 105-116):
```c
pLayerCfg.WindowX0 = 0;
pLayerCfg.WindowX1 = 800;  // Full width
pLayerCfg.WindowY0 = 0;
pLayerCfg.WindowY1 = 480;  // Full height
pLayerCfg.PixelFormat = LTDC_PIXEL_FORMAT_RGB565;
pLayerCfg.Alpha = 255;
pLayerCfg.Alpha0 = 0;
pLayerCfg.BlendingFactor1 = LTDC_BLENDING_FACTOR1_PAxCA;
pLayerCfg.BlendingFactor2 = LTDC_BLENDING_FACTOR2_PAxCA;
pLayerCfg.FBStartAdress = 0xC0000000;  // Use external SDRAM for 800x480x2=768KB
pLayerCfg.ImageWidth = 800;
pLayerCfg.ImageHeight = 480;
```

**Warning**: This requires 768KB, so you MUST use external SDRAM at 0xC0000000.

### Option B: Keep 480x272 Centered (Recommended for Internal RAM)

Keep your current Layer 0 config but add explicit enable:

```c
/* After HAL_LTDC_ConfigLayer in USER CODE BEGIN LTDC_Init 2 */

/* Enable LTDC Layer 0 */
__HAL_LTDC_LAYER_ENABLE(&hltdc, 0);

/* Reload configuration */
__HAL_LTDC_RELOAD_CONFIG(&hltdc);
```

---

## Test #4: Simple Fill Test

Add this debug code to `main.c` after `UI_RenderInit()`:

```c
/* USER CODE BEGIN 2 */
UI_RenderInit();

/* DEBUG: Fill entire framebuffer with RED to test if display works */
uint16_t *fb = (uint16_t *)0x24000000;
for (int i = 0; i < 480 * 272; i++) {
    fb[i] = 0xF800;  // RED in RGB565
}

/* Wait to see red screen */
HAL_Delay(2000);

/* USER CODE END 2 */
```

**Expected Result**: 
- If you see RED, framebuffer works but UI rendering has a bug
- If still blank, LTDC/display hardware not initialized

---

## Recommended Debugging Order:

1. ✅ **Test #2** - Add LCD backlight code (CRITICAL)
2. ✅ **Test #4** - Simple fill test (verifies framebuffer path)
3. ✅ **Test #1** - Disable DMA2D (isolate issue)
4. ✅ **Test #3** - Fix LTDC timing

---

## Common STM32H735G-DK Display Pins:

Check your board User Manual (UM2679) for exact pins:
- **LCD Backlight**: Often PK3 or controlled via I2C
- **LCD Enable**: May be connected to other GPIO
- **Display Power**: Check if powered by 3.3V or needs separate enable

Let me know which test reveals output!
