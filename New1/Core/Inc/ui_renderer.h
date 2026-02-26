#ifndef UI_RENDERER_H
#define UI_RENDERER_H

#include "generated_ui.h"

void UI_Render(void);

/* These must be implemented in your display driver */
void LCD_DrawRect(int x, int y, int w, int h, uint16_t color);
void LCD_DrawOval(int x, int y, int w, int h, uint16_t color);
void LCD_DrawText(int x, int y, char *text, uint16_t color);

#endif
