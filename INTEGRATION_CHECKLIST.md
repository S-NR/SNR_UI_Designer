# STM32H7 UI Integration Checklist

## 🚀 Quick-Start Integration

Complete these steps in order to integrate the UI code with STM32H7 hardware.

---

## ✅ Phase 1: Preparation

- [ ] Review `STM32_INTEGRATION_GUIDE.md` for architecture overview
- [ ] Understand the separation:
  - `New1/Core/` = Portable UI code (DO NOT MODIFY)
  - `UI designer/UI_Designer/` = STM32 HAL code
  - Integration files = Bridge between them
- [ ] Backup your STM32 project:
  ```bash
  cp -r UI_Designer UI_Designer.backup
  ```

---

## ✅ Phase 2: Copy Integration Files

### Copy STM Integration Layer
```bash
# From workspace root:

# Copy header
cp New1/Core/Inc/ui_stm_integration.h \
   UI\ designer/UI_Designer/Core/Inc/

# Copy implementation
cp New1/Core/Src/ui_stm_integration.c \
   UI\ designer/UI_Designer/Core/Src/

# Copy linker documentation
cp New1/Core/Inc/linker_sdram_config.h \
   UI\ designer/UI_Designer/Core/Inc/
```

### Copy Enhanced Renderer
```bash
# Copy new STM32-optimized renderer
cp New1/Core/Src/ui_renderer_stm.c \
   UI\ designer/UI_Designer/Core/Src/ui_renderer.c
```

### Copy UI Interface (if not present)
```bash
# Check if generated_ui.h exists
ls UI\ designer/UI_Designer/Core/Inc/generated_ui.h

# If not, copy:
cp New1/Core/Inc/generated_ui.h \
   UI\ designer/UI_Designer/Core/Inc/

cp New1/Core/Src/generated_ui.c \
   UI\ designer/UI_Designer/Core/Src/
```

**After copying**, your STM32 project structure should look like:
```
UI_Designer/Core/
├── Inc/
│   ├── main.h                      (STM32 standard)
│   ├── generated_ui.h              (UI object definitions) ← NEW
│   ├── ui_renderer.h               (STM32 rendering)      ← NEW
│   ├── ui_stm_integration.h        (Hardware bridge)      ← NEW
│   ├── linker_sdram_config.h       (Linker guide)         ← NEW
│   └── [other driver .h files]
└── Src/
    ├── main.c                      (STM32 standard - MODIFIED)
    ├── generated_ui.c              (UI data)              ← NEW
    ├── ui_renderer.c               (Rendering engine)     ← NEW
    ├── ui_stm_integration.c        (Hardware abstraction) ← NEW
    └── [other driver .c files]
```

- [ ] Files copied to `UI_Designer/Core/Inc/`
- [ ] Files copied to `UI_Designer/Core/Src/`
- [ ] Verify count: ~4 new header files, ~3 new source files

---

## ✅ Phase 3: Linker Script Update

### Locate Linker Script
```bash
find UI_Designer -name "*.ld" | head -1
# Usually: UI_Designer/STM32H743ZITx_FLASH.ld
```

### Add SDRAM Memory Section

Find the `MEMORY` block (top of .ld file) and add:

```ld
MEMORY
{
  DTCMRAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 128K
  RAM (xrw)       : ORIGIN = 0x20020000, LENGTH = 384K
  ITCMRAM (xrw)   : ORIGIN = 0x00000000, LENGTH = 64K
  FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 2048K
  
  /* ADD THIS LINE: */
  SDRAM (xrw)     : ORIGIN = 0xC0000000, LENGTH = 32M
}
```

**Save and verify** the change is present.

- [ ] SDRAM memory section added to MEMORY block

### Add SDRAM Sections

Find the `SECTIONS` block and add before closing `}`:

```ld
  /* SDRAM section for framebuffer and other data */
  .sdram (NOLOAD) :
  {
    . = ALIGN(4);
    _sdram_start = .;
    *(SORT(.sdram*))
    . = ALIGN(4);
    _sdram_end = .;
  } > SDRAM AT > SDRAM
```

**Save and verify** the section is properly formatted.

- [ ] SDRAM sections block added to SECTIONS
- [ ] Linker script syntax verified (no errors)

---

## ✅ Phase 4: STMCubeMX Configuration

### Open STMCubeMX

1. File → Open → Select `UI_Designer/UI_Designer.ioc`
2. **Verify these peripherals are enabled:**

- [ ] **FMC** (Flexible Memory Controller)
  - Mode: SDRAM
  - Settings: Check configuration matches your board
  
- [ ] **LTDC** (LCD-TFT Controller)
  - Configured for your display resolution
  - Timing parameters set correctly
  
- [ ] **DMA2D** (Chrom-ART 2D Accelerator)
  - Enabled (for hardware acceleration)
  
- [ ] **GPIO**
  - Display signal pins configured
  - All LTDC pins assigned

### Generate Code

⚠️ **CRITICAL**: Don't overwrite modified files!

1. Project → Generate Code
2. **Option A** (Recommended):
   - Save generated files separately
   - Manually merge only the peripheral init functions
   
3. **Option B** (If projects don't exist yet):
   - Allow overwrite
   - Then re-apply the UI rendering code

- [ ] STMCubeMX code generated
- [ ] Verified main.c/h hasn't broken UI code
- [ ] Peripheral init functions present

---

## ✅ Phase 5: Include Path Configuration

### Add UI Headers to Include Path

**In your IDE/Makefile:**

Ensure these directories are in the include path:
```
-IRF_Designer/Core/Inc
-IRF_Designer/Core/Inc/generated_ui.h
```

Most IDEs auto-detect, but verify:

- [ ] All `.h` files in `Core/Inc/` can be included
- [ ] No "file not found" errors on `#include "ui_renderer.h"`

---

## ✅ Phase 6: Verify Main Loop

Check your `main.c` has been updated with:

```c
/* After HAL_Init() and peripheral initialization */
UI_FramebufferInit();
UI_RenderInit();

/* In main loop: */
while (1) {
    UI_Render();
    HAL_Delay(16);  /* ~60 FPS */
}
```

If not present, add these manually:

- [ ] UI initialization in main()
- [ ] UI_Render() call in main loop
- [ ] HAL_Delay(16) for FPS control

---

## ✅ Phase 7: Build Project

### Build Command

```bash
cd UI_Designer
make clean
make -j4
```

Or in IDE: **Build Project** (Ctrl+B)

### Verify Build

```bash
# Should show no errors, only warnings if any
# Look for:
# - ✅ Compilation successful
# - ✅ No undefined references to UI functions
# - ✅ Linker script applied correctly
# - ✅ Framebuffer placed in SDRAM
```

Check for these specific errors:

- ❌ "undefined reference to `UI_Render`" → `ui_renderer.c` not compiled
- ❌ "undefined reference to `ui_objects`" → `generated_ui.c` not compiled
- ❌ Linker warnings about SDRAM section → Linker script not updated
- ❌ "section `.sdram' will not fit" → SDRAM size too small

**Fix any errors** before proceeding.

- [ ] Build completes with no errors
- [ ] `.elf` file created in `build/` directory
- [ ] Warnings reviewed and acceptable

---

## ✅ Phase 8: Flash to Board

### Prerequisite
- ST-Link debugger connected to board
- STM32H7 eval board powered on
- USB cable from ST-Link to PC

### Flash Method 1: Command Line
```bash
cd UI_Designer
st-flash write build/UI_Designer.bin 0x08000000
```

### Flash Method 2: STM32CubeProgrammer
1. Launch **STM32CubeProgrammer**
2. Select ST-Link debugger from dropdown
3. Click "Connect"
4. Click "Open file"
5. Select `build/UI_Designer.elf`
6. Click "Download"
7. Wait for "Download completed successfully"

### Flash Method 3: IDE Debugger
1. In IDE: **Debug** or **Run as → Run on Device**
2. IDE will compile and auto-flash

- [ ] Board successfully flashed
- [ ] No timeout or connection errors
- [ ] Console shows "Download successful" or similar

---

## ✅ Phase 9: Test Display

### Initial Verification
1. Look at TFT display connected to STM32 board
2. **Expected**: UI renders on screen (rectangles, text, ovals)
3. **FPS**: Should see smooth updates (~60 FPS)

### Troubleshoot Display

**If display shows white/blank:**
- Check SDRAM init (LED status?)
- Check LTDC is outputting signal (probe LTDC_CLK with scope)
- Check LCD backlight is on
- Reboot board

**If display shows garbage:**
- Check SDRAM timing in STMCubeMX
- Verify linker script SDRAM address
- Disable cache: Set `SCB->DACR = 0;` in main()

**If very slow (< 30 FPS):**
- Enable DMA2D (should be automatic)
- Reduce object count
- Check STM32 clock (should be 550 MHz)

- [ ] Display shows UI elements
- [ ] No flickering or artifacts
- [ ] Framerate is ~60 FPS (watch for smooth animation)

---

## ✅ Phase 10: Validation Tests

Run these quick tests to verify integration:

### Test 1: Rendering Test
```c
/* In main loop, add temporary test code: */
static int test_color = 0;
ui_objects[0].fill = (0xF800 + test_color) & 0xFFFF;  /* Red + shift */
test_color = (test_color + 1) & 0x7FF;
```
**Expected**: Rectangle color cycles through palette

- [ ] Rectangle color changes in real-time

### Test 2: Text Update Test
```c
/* Modify text at runtime: */
static int counter = 0;
sprintf(ui_objects[1].text, "Count: %d", counter++);
```
**Expected**: Text updates on screen

- [ ] Text changes smoothly

### Test 3: FPS Counter
```c
/* Print FPS to serial/console: */
printf("FPS: %lu\n", UI_GetFPS());
```
**Expected**: ~60 FPS printed

- [ ] FPS reads ~60

### Test 4: Hardware Acceleration
Comment out in `ui_stm_integration.c`:
```c
// #define STM32H7_DMA2D_ENABLE
```
Rebuild and compare frame update speed.
**Expected**: Much slower without DMA2D

- [ ] Confirmed DMA2D acceleration working

- [ ] All validation tests pass

---

## ✅ Phase 11: Generate UI Code from Designer

### Use ui_builder.py to Create UI

1. Run **ui_builder.py**
2. Create new project
3. Add UI elements (rectangles, ovals, text)
4. Click **"Generate C Code"**
5. Choose project directory: `UI_Designer/`

### Generated Files
The tool creates/updates:
- `Core/Inc/generated_ui.h` - UI structure (UNCHANGED)
- `Core/Src/generated_ui.c` - UI data (UPDATED)
- `Core/Inc/ui_renderer.h` - Rendering config (UPDATED)
- `Core/Src/ui_renderer.c` - Rendering engine (UPDATED)

⚠️ **Save your STM modifications** before code generation!

- [ ] Created UI design in ui_builder.py
- [ ] Generated C code
- [ ] Merged with existing project if needed

---

## ✅ Final: Complete Integration

All steps completed! Your STM32H7 now:

✅ Runs U rendering engine
✅ Displays on LTDC screen
✅ Uses hardware acceleration (DMA2D)
✅ Updates at 60 FPS
✅ Can be designed with ui_builder.py

---

## 📚 Reference Files

| File | Purpose | Status |
|------|---------|--------|
| `STM32_INTEGRATION_GUIDE.md` | Detailed architecture & setup | ✅ Guide |
| `INTEGRATION_CHECKLIST.md` | This file - step-by-step | ✅ Checklist |
| `INTEGRATION\_NOTES.md` | Generated during export | ℹ️ Auto-generated |
| `ui_stm_integration.h/c` | Hardware abstraction layer | ✅ New |
| `linker_sdram_config.h` | Linker script documentation | ✅ New |

---

## 🆘 Support

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| "undefined reference" errors | Verify all `.c` files in Makefile/IDE |
| Linker errors about SDRAM | Update .ld file with SDRAM section |
| Blank/garbage display | Check SDRAM init, LTDC timing |
| Very slow rendering | Enable DMA2D acceleration |
| Build fails | Clean and rebuild: `make clean && make` |

See `STM32_INTEGRATION_GUIDE.md` troubleshooting section for more.

---

**Status**: ✅ Integration Complete  
**Last Updated**: February 26, 2026  
**Next Step**: Design your UI and generate code!
