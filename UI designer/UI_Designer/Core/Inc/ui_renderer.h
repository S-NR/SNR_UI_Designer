#ifndef UI_RENDERER_H
#define UI_RENDERER_H

#include "generated_ui.h"
#include <stdint.h>

/* ===============================
   RENDER BACKEND SELECTION
   =============================== */

#define UI_RENDER_BACKEND_LCD      1
#define UI_RENDER_BACKEND_LTDC     2

/* >>> SELECT YOUR MODE HERE <<< */
#define UI_RENDER_BACKEND UI_RENDER_BACKEND_LCD

#if UI_RENDER_BACKEND == UI_RENDER_BACKEND_LTDC
#define LCD_WIDTH   800
#define LCD_HEIGHT  480
#endif

void UI_Render(void);

#endif
