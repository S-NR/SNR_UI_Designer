#include "ui_renderer.h"

void UI_Render(void)
{
    for(int i = 0; i < UI_OBJECT_COUNT; i++)
    {
        switch(ui_objects[i].type)
        {
            case UI_RECTANGLE:
                LCD_DrawRect(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].width,
                    ui_objects[i].height,
                    ui_objects[i].fill
                );
                break;

            case UI_OVAL:
                LCD_DrawOval(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].width,
                    ui_objects[i].height,
                    ui_objects[i].fill
                );
                break;

            case UI_TEXT:
                LCD_DrawText(
                    ui_objects[i].x,
                    ui_objects[i].y,
                    ui_objects[i].text,
                    ui_objects[i].fill
                );
                break;
        }
    }
}
