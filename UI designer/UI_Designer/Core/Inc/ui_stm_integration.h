/**
 * @file ui_stm_integration.h
 * @brief STM32 HAL Integration Layer for UI Rendering System
 * @details Provides hardware abstraction for LTDC display, DMA2D acceleration,
 *          and framebuffer management for STM32H7 series.
 * @date 2026
 */

#ifndef UI_STM_INTEGRATION_H
#define UI_STM_INTEGRATION_H

#include <stdint.h>
#include <stddef.h>

/* ===================================================================
   FRAMEBUFFER CONFIGURATION FOR STM32H7
   =================================================================== */

/* Define LTDC/LCD dimensions (typically 800x480 for STM32H7 eval boards) */
#define LTDC_WIDTH          800
#define LTDC_HEIGHT         480

/* RGB565 format: 2 bytes per pixel */
#define LTDC_BYTES_PER_PIXEL 2
#define LTDC_BUFFER_SIZE     (LTDC_WIDTH * LTDC_HEIGHT * LTDC_BYTES_PER_PIXEL)

/* Framebuffer locations in SDRAM */
/* FMC SDRAM starts at 0xC0000000 for STM32H7 */
#define SDRAM_BASE_ADDR      0xC0000000
#define FRAMEBUFFER_LAYER0   ((uint16_t *)(SDRAM_BASE_ADDR + 0x00000000))  /* Layer 0 */
#define FRAMEBUFFER_LAYER1   ((uint16_t *)(SDRAM_BASE_ADDR + 0x00180000))  /* Layer 1 (offset) */

/* ===================================================================
   DMA2D HARDWARE ACCELERATION
   =================================================================== */

#ifdef STM32H7_DMA2D_ENABLE
/**
 * @brief Hardware-accelerated rectangle fill using DMA2D
 * @param x,y: Start coordinates
 * @param w,h: Width and height
 * @param color: RGB565 color value
 */
void DMA2D_FillRect(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Wait for DMA2D operation to complete
 */
void DMA2D_WaitComplete(void);

#endif

/* ===================================================================
   FRAMEBUFFER OPERATIONS
   =================================================================== */

/**
 * @brief Initialize framebuffer and display hardware
 * Configures LTDC, DMA2D, and SDRAM for rendering
 */
void UI_FramebufferInit(void);

/**
 * @brief Clear entire framebuffer to color
 */
void UI_FramebufferClear(uint16_t color);

/**
 * @brief Swap framebuffers (double-buffering)
 * @note Requires configured LTDC interrupts
 */
void UI_FramebufferSwap(void);

/**
 * @brief Get current active framebuffer pointer
 */
uint16_t* UI_GetFramebuffer(void);

/**
 * @brief Write pixel to framebuffer
 * @param x,y: Pixel coordinates
 * @param color: RGB565 color
 */
static inline void UI_DrawPixel(int x, int y, uint16_t color)
{
    if (x >= 0 && x < LTDC_WIDTH && y >= 0 && y < LTDC_HEIGHT) {
        uint16_t *fb = UI_GetFramebuffer();
        fb[y * LTDC_WIDTH + x] = color;
    }
}

/* ===================================================================
   RENDERING FUNCTIONS (STM Hardware Optimized)
   =================================================================== */

/**
 * @brief Draw filled rectangle (hardware accelerated if available)
 */
void UI_DrawFilledRect(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Draw rectangle outline
 */
void UI_DrawRectOutline(int x, int y, int w, int h, uint16_t color, int thickness);

/**
 * @brief Draw filled circle/oval (software implementation)
 */
void UI_DrawFilledOval(int x, int y, int w, int h, uint16_t color);

/**
 * @brief Draw text using system font
 * @param x,y: Top-left position
 * @param text: Null-terminated string
 * @param color: Text color (RGB565)
 * @param size: Font size (12, 16, 20, 24 supported)
 */
void UI_DrawText(int x, int y, const char *text, uint16_t color, int size);

/* ===================================================================
   UI RENDERING (Main Entry Point)
   =================================================================== */

/**
 * @brief Render entire UI from ui_objects array
 * Call this from main loop at desired frame rate (typically 30-60 FPS)
 */
void UI_RenderFrame(void);

/**
 * @brief Update display from framebuffer (LTDC refresh)
 * Called automatically by LTDC VSYNC interrupt
 */
void UI_DisplayUpdate(void);

/* ===================================================================
   UTILITIES
   =================================================================== */

/**
 * @brief Convert RGB888 color to RGB565 format
 */
uint16_t UI_RGB888_to_RGB565(uint8_t r, uint8_t g, uint8_t b);

/**
 * @brief Get tick counter for FPS/timing
 */
uint32_t UI_GetTicks(void);

#endif /* UI_STM_INTEGRATION_H */
