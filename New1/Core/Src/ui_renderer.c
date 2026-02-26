#include "ui_renderer.h"
#include "ui_stm_integration.h"

#ifdef STM32H7xx
#include "stm32h7xx_hal.h"
#include "ltdc.h"
#include "dma2d.h"
#endif

/* Framebuffer in SDRAM (STM32H7 configuration) */
__attribute__((section(".sdram")))
uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

static uint32_t g_FrameCounter = 0;
static uint32_t g_LastFrameTime = 0;
static uint32_t g_FPS = 0;

/* Helper: Draw pixel to framebuffer */
static void draw_pixel(int x, int y, uint16_t color)
{
    if (x >= 0 && x < LCD_WIDTH && y >= 0 && y < LCD_HEIGHT)
        framebuffer[y * LCD_WIDTH + x] = color;
}

/* Helper: Draw filled rectangle (hardware accelerated if available) */
static void draw_filled_rect(int x, int y, int w, int h, uint16_t color)
{
    /* Clip to bounds */
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > LCD_WIDTH) w = LCD_WIDTH - x;
    if (y + h > LCD_HEIGHT) h = LCD_HEIGHT - y;
    
    if (w <= 0 || h <= 0) return;

#ifdef STM32H7_DMA2D_ENABLE
    /* Use DMA2D for hardware acceleration */
    DMA2D_FillRect(x, y, w, h, color);
#else
    /* Software fallback */
    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            draw_pixel(px, py, color);
        }
    }
#endif
}

/* Helper: Draw rectangle outline */
static void draw_rect_outline(int x, int y, int w, int h, uint16_t color)
{
    draw_filled_rect(x, y, w, 1, color);                    /* Top */
    draw_filled_rect(x, y + h - 1, w, 1, color);            /* Bottom */
    draw_filled_rect(x, y, 1, h, color);                    /* Left */
    draw_filled_rect(x + w - 1, y, 1, h, color);            /* Right */
}

/* Helper: Draw filled ellipse/oval */
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
        for (int py = y_center - y_curr; py <= y_center + y_curr; py++) {
            draw_pixel(x_center + x_curr, py, color);
            if (x_curr > 0)
                draw_pixel(x_center - x_curr, py, color);
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

void UI_ClearBuffer(uint16_t color)
{
    uint32_t *p32 = (uint32_t *)framebuffer;
    uint32_t color32 = (color << 16) | color;
    
    for (size_t i = 0; i < (LCD_WIDTH * LCD_HEIGHT / 2); i++) {
        p32[i] = color32;
    }
}

void UI_RenderInit(void)
{
    /* Initialize framebuffer and display system */
    UI_FramebufferInit();
    UI_ClearBuffer(0xFFFF);  /* Clear to white */
    g_LastFrameTime = HAL_GetTick();
    g_FrameCounter = 0;
}

void UI_Render(void)
{
    /* Clear framebuffer */
    UI_ClearBuffer(0xFFFF);  /* White background */
    
    /* Render all UI objects */
    for (int i = 0; i < UI_OBJECT_COUNT; i++) {
        UI_Object *obj = &ui_objects[i];
        
        switch (obj->type) {
            case UI_RECTANGLE:
                draw_filled_rect(obj->x, obj->y, obj->width, obj->height, obj->fill);
                if (obj->outline != 0x0000) {
                    draw_rect_outline(obj->x, obj->y, obj->width, obj->height, obj->outline);
                }
                break;
                
            case UI_OVAL:
                draw_filled_ellipse(obj->x, obj->y, obj->width, obj->height, obj->fill);
                break;
                
            case UI_TEXT:
                if (obj->text[0] != '\0') {
                    /* Simple text rendering - can be enhanced */
                    UI_DrawText(obj->x, obj->y, obj->text, obj->fill, obj->font_size);
                }
                break;
                
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
}

uint16_t* UI_GetFramebufferPtr(void)
{
    return framebuffer;
}

uint32_t UI_GetFPS(void)
{
    return g_FPS;
}
