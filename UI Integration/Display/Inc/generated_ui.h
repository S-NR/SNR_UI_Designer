#ifndef GENERATED_UI_H
#define GENERATED_UI_H

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

extern UI_Object ui_objects[UI_OBJECT_COUNT];

#endif
