#ifndef UI_RENDERER_H
#define UI_RENDERER_H

#include "generated_ui.h"
#include <stdint.h>

/* UI Rendering Backend Modes */
#define UI_RENDER_BACKEND_LCD      1
#define UI_RENDER_BACKEND_LTDC     2

/* Select LTDC for STM32H7 with hardware acceleration */
#define UI_RENDER_BACKEND UI_RENDER_BACKEND_LTDC

/* LTDC Configuration */
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
#define LCD_WIDTH   800
#define LCD_HEIGHT  480
#define LCD_BYTES_PER_PIXEL 2  /* RGB565 format */

/* Enable DMA2D hardware acceleration (optional) */
#define STM32H7_DMA2D_ENABLE
#endif

/* Main Rendering Functions */
void UI_Render(void);
void UI_RenderInit(void);
void UI_ClearBuffer(uint16_t color);
uint16_t* UI_GetFramebufferPtr(void);
uint32_t UI_GetFPS(void);

#endif
