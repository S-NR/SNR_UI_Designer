# UI Code Integration Guide for STM32H7

## Files Generated
- `generated_ui.h/c` - UI object definitions (DO NOT MODIFY)
- `ui_renderer.h/c` - STM32H7 rendering engine (optimized for LTDC + DMA2D)
- `ui_layout.c` - Layout utilities for future expansion

## Integration Steps

### 1. Copy Files to STM32 Project
Copy the generated files to your STM32CubeMX project:
```
UI_Designer/
└── Core/
    ├── Inc/
    │   ├── generated_ui.h
    │   ├── ui_renderer.h
    │   ├── ui_stm_integration.h  (Already created)
    │   └── linker_sdram_config.h (Reference for linker script)
    └── Src/
        ├── generated_ui.c
        ├── ui_renderer.c
        ├── ui_stm_integration.c   (Already created)
        └── ui_layout.c
```

### 2. Update Linker Script (.ld file)
Add SDRAM section for framebuffer:
```ld
MEMORY
{
  /* ... existing sections ... */
  SDRAM (xrw)     : ORIGIN = 0xC0000000, LENGTH = 32M
}

SECTIONS
{
  /* ... existing sections ... */
  
  .sdram (NOLOAD) :
  {
    . = ALIGN(4);
    *(SORT(.sdram*))
    . = ALIGN(4);
  } > SDRAM AT > SDRAM
}
```

### 3. Update main.h Includes
The main.h has been auto-updated with:
```c
#include "generated_ui.h"
#include "ui_renderer.h"
#include "ui_stm_integration.h"
```

### 4. Update main.c
The main.c has been auto-updated with:
```c
/* In initialization section (USER CODE BEGIN 2) */
UI_FramebufferInit();
UI_RenderInit();

/* In main loop (USER CODE BEGIN WHILE) */
while (1) {
    UI_Render();
    HAL_Delay(16);  /* ~60 FPS */
}
```

### 5. Build Configuration
- Ensure STMCubeMX has LTDC and DMA2D initialized
- Ensure SDRAM is properly configured (FMC)
- Linker script points to correct SDRAM addresses

### 6. Display Backend Selection
In `ui_renderer.h`, select rendering backend:
- `UI_RENDER_BACKEND_LCD` - For external LCD driver
- `UI_RENDER_BACKEND_LTDC` - For STM32 LTDC controller (RECOMMENDED)

### 7. Hardware Acceleration (Optional)
DMA2D acceleration is enabled by default when using LTDC.
Disable in `ui_renderer.h` if needed:
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
   - Located in SDRAM (0xC0000000)
   - 800x480 RGB565 = 768 KB
   - Ensure SDRAM is large enough

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
