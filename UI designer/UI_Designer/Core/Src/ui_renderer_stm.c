/**
 * @file ui_renderer.c
 * @brief STM32H7 Optimized UI Rendering Engine
 * @details Renders UI objects to LTDC display with DMA2D acceleration
 * 
 * This file integrates the portable generated_ui.h objects with STM32
 * hardware capabilities for fast, efficient rendering.
 */

#include "ui_renderer.h"
#include "ui_stm_integration.h"
#include "generated_ui.h"

#ifdef STM32H7xx
#include "stm32h7xx_hal.h"
#include "ltdc.h"
#include "dma2d.h"
#endif

/* ===================================================================
   RENDER BACKEND SELECTION
   =================================================================== */

#define UI_RENDER_BACKEND UI_RENDER_BACKEND_LTDC  /* Use LTDC on STM32H7 */

/* ===================================================================
   LTDC FRAMEBUFFER CONFIGURATION
   =================================================================== */

#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC

#define LCD_WIDTH   800
#define LCD_HEIGHT  480

/* Framebuffer placed in SDRAM by linker script */
/* FMC SDRAM starts at 0xC0000000 for STM32H7 */
__attribute__((section(".sdram")))
uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

#endif

/* ===================================================================
   RENDERING STATE
   =================================================================== */

static uint32_t g_FrameCounter = 0;
static uint32_t g_LastFrameTime = 0;
static uint32_t g_FPS = 0;

/* ===================================================================
   PIXEL DRAWING (Core primitive)
   =================================================================== */

static void draw_pixel(int x, int y, uint16_t color)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    if (x >= 0 && x < LCD_WIDTH && y >= 0 && y < LCD_HEIGHT) {
        framebuffer[y * LCD_WIDTH + x] = color;
    }
#endif
}

/* ===================================================================
   SHAPE DRAWING (Filled primitives)
   =================================================================== */

static void draw_filled_rect(int x, int y, int w, int h, uint16_t color)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    
    /* Clip to screen bounds */
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > LCD_WIDTH) w = LCD_WIDTH - x;
    if (y + h > LCD_HEIGHT) h = LCD_HEIGHT - y;
    
    if (w <= 0 || h <= 0) return;
    
    #ifdef STM32H7_DMA2D_ENABLE
    /* Try hardware acceleration first */
    DMA2D_FillRect(x, y, w, h, color);
    DMA2D_WaitComplete();
    #else
    /* Software implementation */
    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            draw_pixel(px, py, color);
        }
    }
    #endif
    
#endif
}

/**
 * @brief Draw rectangle outline
 */
static void draw_rect_outline(int x, int y, int w, int h, uint16_t color, int thickness)
{
    /* Top edge */
    draw_filled_rect(x, y, w, thickness, color);
    /* Bottom edge */
    draw_filled_rect(x, y + h - thickness, w, thickness, color);
    /* Left edge */
    draw_filled_rect(x, y, thickness, h, color);
    /* Right edge */
    draw_filled_rect(x + w - thickness, y, thickness, h, color);
}

/**
 * @brief Draw filled circle/ellipse using Midpoint algorithm
 */
static void draw_filled_ellipse(int x, int y, int w, int h, uint16_t color)
{
    int x_center = x + w / 2;
    int y_center = y + h / 2;
    int a = w / 2;
    int b = h / 2;
    
    if (a <= 0 || b <= 0) return;
    
    int a2 = a * a;
    int b2 = b * b;
    int x_curr = 0;
    int y_curr = b;
    int d = b2 + a2 / 4 - a2 * b;
    
    while (x_curr * b2 < y_curr * a2) {
        /* Draw vertical line at X */
        for (int py = y_center - y_curr; py <= y_center + y_curr; py++) {
            draw_pixel(x_center + x_curr, py, color);
            if (x_curr > 0) {
                draw_pixel(x_center - x_curr, py, color);
            }
        }
        
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
   TEXT RENDERING
   =================================================================== */

/**
 * @brief Simple text rendering with basic font
 * @param x,y: Position
 * @param text: Text string
 * @param color: RGB565 color
 */
static void draw_text(int x, int y, const char *text, uint16_t color)
{
    if (!text) return;
    
    /* Simple implementation: draw text as filled blocks */
    int char_width = 8;
    int char_height = 12;
    int x_pos = x;
    
    while (*text) {
        if (*text == '\n') {
            x_pos = x;
            y += char_height;
        } else if (*text >= 32 && *text <= 126) {
            /* Draw character placeholder */
            draw_filled_rect(x_pos, y, char_width, char_height, color);
            x_pos += char_width;
        }
        text++;
    }
}

/* ===================================================================
   COLOR CONVERSION
   =================================================================== */

static uint16_t rgb888_to_rgb565(uint32_t rgb888)
{
    uint8_t r = (rgb888 >> 16) & 0xFF;
    uint8_t g = (rgb888 >> 8) & 0xFF;
    uint8_t b = rgb888 & 0xFF;
    
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3);
}

/* ===================================================================
   MAIN RENDERING FUNCTIONS
   =================================================================== */

/**
 * @brief Clear framebuffer to color
 */
void UI_ClearBuffer(uint16_t color)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    uint32_t *p32 = (uint32_t *)framebuffer;
    uint32_t color32 = (color << 16) | color;
    
    for (size_t i = 0; i < (LCD_WIDTH * LCD_HEIGHT / 2); i++) {
        p32[i] = color32;
    }
#endif
}

/**
 * @brief Main rendering function - renders all UI objects
 * 
 * This is the primary entry point for rendering the entire UI.
 * Should be called from main loop at desired frame rate.
 */
void UI_Render(void)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    
    /* Clear framebuffer */
    UI_ClearBuffer(0xFFFF);  /* White background */
    
    /* Render each UI object */
    for (int i = 0; i < UI_OBJECT_COUNT; i++) {
        UI_Object *obj = &ui_objects[i];
        
        switch (obj->type) {
        
            case UI_RECTANGLE:
            {
                /* Draw filled rectangle */
                draw_filled_rect(obj->x, obj->y, obj->width, obj->height, obj->fill);
                
                /* Draw outline if not black */
                if (obj->outline != 0x0000) {
                    draw_rect_outline(obj->x, obj->y, obj->width, obj->height, 
                                    obj->outline, 1);
                }
                break;
            }
            
            case UI_OVAL:
            {
                /* Draw filled ellipse/oval */
                draw_filled_ellipse(obj->x, obj->y, obj->width, obj->height, obj->fill);
                break;
            }
            
            case UI_TEXT:
            {
                /* Draw text at specified position */
                if (obj->text[0] != '\0') {
                    draw_text(obj->x, obj->y, obj->text, obj->fill);
                }
                break;
            }
            
            default:
                break;
        }
    }
    
    /* Update frame statistics */
    g_FrameCounter++;
    uint32_t now = HAL_GetTick();
    if (now - g_LastFrameTime >= 1000) {
        g_FPS = g_FrameCounter;
        g_FrameCounter = 0;
        g_LastFrameTime = now;
    }

#endif
}

/**
 * @brief Get current FPS
 */
uint32_t UI_GetFPS(void)
{
    return g_FPS;
}

/**
 * @brief Get framebuffer pointer for direct access
 */
uint16_t* UI_GetFramebufferPtr(void)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    return framebuffer;
#else
    return NULL;
#endif
}

/**
 * @brief Initialize UI rendering system
 * Must be called before first UI_Render() call
 */
void UI_RenderInit(void)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    /* LTDC is initialized by STMCubeMX via MX_LTDC_Init() */
    /* This function performs any additional UI-specific initialization */
    
    /* Clear buffer initially */
    UI_ClearBuffer(0xFFFF);
    
    /* Initialize frame counter */
    g_LastFrameTime = HAL_GetTick();
    g_FrameCounter = 0;
#endif
}
