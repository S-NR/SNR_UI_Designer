#include <stdint.h>

typedef enum {
    UI_RECTANGLE,
    UI_OVAL,
    UI_TEXT
} UI_ObjectType;

typedef struct {
    UI_ObjectType type;
    int x;
    int y;
    int width;
    int height;
    uint16_t fill;
    uint16_t outline;
    int font_size;
    char text[50];
} UI_Object;

#define UI_OBJECT_COUNT 2

UI_Object ui_objects[UI_OBJECT_COUNT] = {
    {UI_RECTANGLE, 211, 136, 100, 50, 0x867D, 0x0000, 0, ""},
    {UI_TEXT, 258, 158, 0, 0, 0x0000, 0x0000, 12, "Sample Text"},
};
