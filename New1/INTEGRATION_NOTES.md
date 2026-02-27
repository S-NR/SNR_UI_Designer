# UI Code Integration Guide for STM32H7

## Files Generated
- `generated_ui.h/c` - UI object definitions (DO NOT MODIFY)
- `ui_renderer.h/c` - STM32H7 rendering engine (optimized for LTDC + DMA2D)
- `ui_layout.c` - Layout utilities for future expansion

## Integration Steps

### 1. Copy Files to STM32 Project
Files are automatically generated in your project's Display folder:
```
UI_Integration/
└── Display/
    ├── Inc/
    │   ├── generated_ui.h
    │   ├── ui_renderer.h
    │   ├── ui_stm_integration.h
    │   └── linker_sdram_config.h (Reference)
    └── Src/
        ├── generated_ui.c
        ├── ui_renderer.c
        ├── ui_stm_integration.c
        └── ui_layout.c
```

### 2. STM32CubeIDE Build Configuration
Ensure Display folder is included in build paths:
- Right-click project → Properties → C/C++ Build → Settings
- Add to Include Paths: `"${workspace_loc:/${ProjName}/Display/Inc}"`
- Verify in .cproject that Display/Src is in source entries

### 3. Framebuffer Configuration (Already Done)
The framebuffer uses internal AXI SRAM at 0x24000000:
- Resolution: 480x272 RGB565 (261 KB)
- Fits in 320KB AXI SRAM D1 domain
- LTDC configured in Core/Src/ltdc.c
- No external SDRAM required

### 4. Update main.c (If Not Already Done)
Add these includes and initialization:
```c
/* USER CODE BEGIN Includes */
#include "ui_renderer.h"
#include "ui_stm_integration.h"
/* USER CODE END Includes */

/* In initialization section (USER CODE BEGIN 2) */
UI_RenderInit();

/* In main loop (USER CODE BEGIN WHILE) */
while (1) {
    UI_Render();
    HAL_Delay(16);  /* ~60 FPS */
    /* USER CODE END WHILE */
}
```

### 5. Build Configuration
- Ensure STM32CubeMX has LTDC and DMA2D initialized
- LTDC Layer 0 must point to 0x24000000 with RGB565 format

### 6. Display Backend Selection
In `ui_renderer.h`, select rendering backend:
- `UI_RENDER_BACKEND_LCD` - For external LCD driver
- `UI_RENDER_BACKEND_LTDC` - For STM32 LTDC controller (RECOMMENDED)

### 7. Hardware Acceleration (Optional)
DMA2D acceleration is enabled by default when using LTDC.
Disable in `ui_stm_integration.h` if needed:
```c
/* Comment out to disable DMA2D */
#define STM32H7_DMA2D_ENABLE
```

## UI Object Properties

### Position & Size
- `x, y` - Top-left corner coordinates
- `width, height` - Dimensions in pixels

### Colors (RGB565 16-bit format)
- `fill` - Fill color (0xRRGGBBB in RGB565)
- `outline` - Border color

### Text Properties  
- `font_size` - Size in pixels (12, 16, 20, 24)
- `text` - Text string (up to 50 characters)

## Example Usage

Modify UI objects at runtime:
```c
/* Change rectangle color */
ui_objects[0].fill = UI_RGB888_to_RGB565(255, 0, 0);  /* Red */

/* Change text */
strcpy(ui_objects[1].text, "New Text");

/* Trigger re-render */
UI_Render();
```

## Performance Tips

1. **FPS Monitoring**
   - Call `UI_GetFPS()` to get framerate
   - Adjust `HAL_Delay(16)` for different target FPS

2. **DMA2D Acceleration**
   - Rectangle fills use hardware DMA2D
   - Much faster than software rendering
   - Ensure DMA2D is initialized by STMCubeMX

3. **Framebuffer Location**
   - Located in internal AXI SRAM (0x24000000)
   - 480x272 RGB565 = 261 KB (fits in 320KB RAM)
   - For higher resolutions, external memory required

## Troubleshooting

**Display shows garbage:**
- Check SDRAM initialization
- Verify framebuffer address in linker script
- Ensure MX_LTDC_Init() called before UI_RenderInit()

**Build errors:**
- Verify all includes are in include paths
- Check STM32CubeMX has generated ltdc.h, dma2d.h
- Ensure linker script has SDRAM section

**Rendering too slow:**
- Disable DMA2D and check framebuffer clearing speed
- Check if SDRAM bandwidth is bottleneck
- Consider using partial updates instead of full refresh

## Future Enhancements

- Multi-layer rendering
- Partial screen updates
- Animation framework
- Widget library (buttons, sliders, etc.)
- Touch input handling
