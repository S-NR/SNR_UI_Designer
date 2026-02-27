#include "ui_renderer.h"

#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LCD

/* ===== LCD DRIVER MODE ===== */
/* User must implement these in display driver */
void LCD_DrawRect(int x, int y, int w, int h, uint16_t color);
void LCD_DrawOval(int x, int y, int w, int h, uint16_t color);
void LCD_DrawText(int x, int y, char *text, uint16_t color);

#elif UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC

#include <string.h>

/* Framebuffer must be placed in SDRAM */
__attribute__((section(".sdram")))
uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

static void draw_pixel(int x, int y, uint16_t color)
{
    if (x >= 0 && x < LCD_WIDTH && y >= 0 && y < LCD_HEIGHT)
        framebuffer[y * LCD_WIDTH + x] = color;
}

static void draw_rect(int x, int y, int w, int h, uint16_t color)
{
    for(int i = 0; i < h; i++)
        for(int j = 0; j < w; j++)
            draw_pixel(x + j, y + i, color);
}

#endif


void UI_Render(void)
{
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
    memset(framebuffer, 0x00, LCD_WIDTH * LCD_HEIGHT * 2);
#endif

    for(int i = 0; i < UI_OBJECT_COUNT; i++)
    {
        switch(ui_objects[i].type)
        {
            case UI_RECTANGLE:
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LCD
                LCD_DrawRect(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].width,
                    ui_objects[i].height,
                    ui_objects[i].fill
                );
#else
                draw_rect(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].width,
                    ui_objects[i].height,
                    ui_objects[i].fill
                );
#endif
                break;

            case UI_TEXT:
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LCD
                LCD_DrawText(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].text,
                    ui_objects[i].fill
                );
#endif
                break;

            case UI_OVAL:
#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LCD
                LCD_DrawOval(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].width,
                    ui_objects[i].height,
                    ui_objects[i].fill
                );
#endif
                break;
        }
    }
}
