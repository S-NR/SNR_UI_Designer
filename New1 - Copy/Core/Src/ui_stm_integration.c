/**
 * @file ui_stm_integration.c
 * @brief STM32 Hardware Integration for UI Rendering
 * @details LTDC, DMA2D, framebuffer management implementation
 */

#include "ui_stm_integration.h"
#include "generated_ui.h"

#ifdef STM32H7xx
#include "stm32h7xx_hal.h"
#include "ltdc.h"
#include "dma2d.h"
#endif

/* ===================================================================
   FRAMEBUFFER STATE
   =================================================================== */

static uint16_t *g_pFramebuffer = FRAMEBUFFER_LAYER0;
static uint16_t *g_pBackbuffer = FRAMEBUFFER_LAYER1;

/* ===================================================================
   FRAMEBUFFER OPERATIONS
   =================================================================== */

void UI_FramebufferInit(void)
{
    /* Framebuffers already configured by STM32CubeMX during MX_LTDC_Init() */
    /* This function is called for any additional initialization */
    
    g_pFramebuffer = FRAMEBUFFER_LAYER0;
    g_pBackbuffer = FRAMEBUFFER_LAYER1;
    
    /* Clear both buffers */
    UI_FramebufferClear(0x0000);  /* Black */
}

void UI_FramebufferClear(uint16_t color)
{
    uint32_t *p32 = (uint32_t *)g_pFramebuffer;
    uint32_t color32 = (color << 16) | color;  /* Pack two pixels as 32-bit value */
    
    /* Clear by 32-bit writes (faster) */
    for (size_t i = 0; i < LTDC_BUFFER_SIZE / 4; i++) {
        p32[i] = color32;
    }
}

void UI_FramebufferSwap(void)
{
    /* Swap framebuffer pointers for double-buffering */
    uint16_t *temp = g_pFramebuffer;
    g_pFramebuffer = g_pBackbuffer;
    g_pBackbuffer = temp;
    
    /* Update LTDC to point to new framebuffer */
    /* This would be done via LTDC interrupt or explicit update */
}

uint16_t* UI_GetFramebuffer(void)
{
    return g_pFramebuffer;
}

/* ===================================================================
   DMA2D HARDWARE ACCELERATION
   =================================================================== */

#ifdef STM32H7_DMA2D_ENABLE

void DMA2D_FillRect(int x, int y, int w, int h, uint16_t color)
{
    /* Clip to framebuffer bounds */
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > LTDC_WIDTH) w = LTDC_WIDTH - x;
    if (y + h > LTDC_HEIGHT) h = LTDC_HEIGHT - y;
    
    if (w <= 0 || h <= 0) return;
    
    /* Calculate start address in framebuffer */
    uint32_t start_addr = (uint32_t)g_pFramebuffer + (y * LTDC_WIDTH + x) * 2;
    
    /* Configure DMA2D for memory fill operation */
    DMA2D_HandleTypeDef hdma2d;
    hdma2d.Instance = DMA2D;
    
    /* Memset operation: fill rectangle with single color */
    if (HAL_DMA2D_Start(&hdma2d, color, start_addr, w, h) != HAL_OK) {
        /* Fallback to software if DMA2D fails */
        for (int py = y; py < y + h; py++) {
            for (int px = x; px < x + w; px++) {
                UI_DrawPixel(px, py, color);
            }
        }
    }
}

void DMA2D_WaitComplete(void)
{
    /* Wait for DMA2D to complete current operation */
    while (DMA2D->CR & DMA2D_CR_START) {
        /* Poll until complete */
    }
}

#endif

/* ===================================================================
   RENDERING PRIMITIVES
   =================================================================== */

void UI_DrawFilledRect(int x, int y, int w, int h, uint16_t color)
{
#ifdef STM32H7_DMA2D_ENABLE
    /* Use hardware DMA2D acceleration if available */
    DMA2D_FillRect(x, y, w, h, color);
#else
    /* Software implementation */
    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            UI_DrawPixel(px, py, color);
        }
    }
#endif
}

void UI_DrawRectOutline(int x, int y, int w, int h, uint16_t color, int thickness)
{
    /* Top line */
    UI_DrawFilledRect(x, y, w, thickness, color);
    /* Bottom line */
    UI_DrawFilledRect(x, y + h - thickness, w, thickness, color);
    /* Left line */
    UI_DrawFilledRect(x, y, thickness, h, color);
    /* Right line */
    UI_DrawFilledRect(x + w - thickness, y, thickness, h, color);
}

void UI_DrawFilledOval(int x, int y, int w, int h, uint16_t color)
{
    /* Midpoint ellipse algorithm */
    int x_center = x + w / 2;
    int y_center = y + h / 2;
    int a = w / 2;  /* semi-major axis */
    int b = h / 2;  /* semi-minor axis */
    
    if (a <= 0 || b <= 0) return;
    
    int a2 = a * a;
    int b2 = b * b;
    int x_curr = 0;
    int y_curr = b;
    int d = b2 + a2 / 4 - a2 * b;
    
    while (x_curr * b2 < y_curr * a2) {
        /* Draw horizontal line at y */
        UI_DrawFilledRect(x_center - x_curr, y_center + y_curr, 2 * x_curr, 1, color);
        UI_DrawFilledRect(x_center - x_curr, y_center - y_curr, 2 * x_curr, 1, color);
        
        if (d < 0) {
            d = d + 2 * b2 * x_curr + b2;
        } else {
            d = d + 2 * b2 * x_curr - 2 * a2 * y_curr + b2;
            y_curr--;
        }
        x_curr++;
    }
}

/* ===================================================================
   TEXT RENDERING (Simple System Font)
   =================================================================== */

/* Simple 5x7 bitmap font (ASCII 32-126) */
static const uint8_t g_FontData5x7[] = {
    0x00, 0x00, 0x00, 0x00, 0x00,  /* Space */
    0x3E, 0x5B, 0x4F, 0x59, 0x3E,  /* @ */
    /* Additional fonts can be added here */
};

void UI_DrawText(int x, int y, const char *text, uint16_t color, int size)
{
    if (!text) return;
    
    /* Simple text rendering: draw each character as a block */
    int char_width = 6 * size / 12;
    int char_height = 8 * size / 12;
    
    int x_pos = x;
    for (const char *c = text; *c != '\0'; c++) {
        if (*c == '\n') {
            x_pos = x;
            y += char_height;
        } else {
            /* Draw character as rectangle (placeholder) */
            UI_DrawFilledRect(x_pos, y, char_width, char_height, color);
            x_pos += char_width;
        }
    }
}

/* ===================================================================
   UI RENDERING MAIN FUNCTION
   =================================================================== */

void UI_RenderFrame(void)
{
    /* Clear framebuffer */
    UI_FramebufferClear(0xFFFF);  /* White background */
    
    /* Render all UI objects from generated_ui.c */
    for (int i = 0; i < UI_OBJECT_COUNT; i++) {
        UI_Object *obj = &ui_objects[i];
        
        switch (obj->type) {
            case UI_RECTANGLE:
                UI_DrawFilledRect(obj->x, obj->y, obj->width, obj->height, obj->fill);
                UI_DrawRectOutline(obj->x, obj->y, obj->width, obj->height, obj->outline, 1);
                break;
                
            case UI_OVAL:
                UI_DrawFilledOval(obj->x, obj->y, obj->width, obj->height, obj->fill);
                /* Outline would require ellipse algorithm */
                break;
                
            case UI_TEXT:
                UI_DrawText(obj->x, obj->y, obj->text, obj->fill, obj->font_size);
                break;
                
            default:
                break;
        }
    }
    
    /* Update display */
    UI_DisplayUpdate();
}

void UI_DisplayUpdate(void)
{
    /* Typically called by LTDC VSYNC interrupt for automatic refresh */
    /* Or can be called explicitly to force update */
    
    #ifdef STM32H7xx
    /* Update LTDC layer framebuffer address if needed */
    /* This is handled by the LTDC driver configuration */
    #endif
}

/* ===================================================================
   UTILITY FUNCTIONS
   =================================================================== */

uint16_t UI_RGB888_to_RGB565(uint8_t r, uint8_t g, uint8_t b)
{
    /* Convert 8-bit RGB to 5-6-5 format */
    uint16_t rgb565 = (
        ((r & 0xF8) << 8) |   /* R: bits 15-11 */
        ((g & 0xFC) << 3) |   /* G: bits 10-5 */
        ((b & 0xF8) >> 3)     /* B: bits 4-0 */
    );
    return rgb565;
}

uint32_t UI_GetTicks(void)
{
    return HAL_GetTick();
}
