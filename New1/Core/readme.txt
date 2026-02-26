ensure you have low level functions

void LCD_DrawPixel(int x, int y, uint16_t color);
void LCD_FillRect(int x, int y, int w, int h, uint16_t color);
void LCD_DrawRect(int x, int y, int w, int h, uint16_t color);
void LCD_DrawChar(int x, int y, char c, uint16_t color);
void LCD_DrawString(int x, int y, char *str, uint16_t color);
void LCD_DrawCircle(int x, int y, int radius, uint16_t color);


These typically exist in:

ILI9341 drivers

ST7789 drivers

LTDC HAL-based systems

TouchGFX low-level layers