# 🚀 Quick Start - STM32H7 UI Integration

**Time to integrate: ~2-3 hours (first time)**

---

## 1️⃣ Copy Files (5 min)

```bash
# Navigate to workspace
cd e:/GIT/SNR_UI_Designer

# Copy integration header & implementation
cp New1/Core/Inc/ui_stm_integration.h "UI designer/UI_Designer/Core/Inc/"
cp New1/Core/Src/ui_stm_integration.c "UI designer/UI_Designer/Core/Src/"

# Copy enhanced renderer
cp New1/Core/Src/ui_renderer_stm.c "UI designer/UI_Designer/Core/Src/ui_renderer.c"

# Copy linker documentation
cp New1/Core/Inc/linker_sdram_config.h "UI designer/UI_Designer/Core/Inc/"
```

---

## 2️⃣ Update Linker Script (10 min)

**File**: `UI_Designer/STM32H743ZITx_FLASH.ld` (or your board's .ld)

**Find MEMORY section and add**:
```ld
SDRAM (xrw)     : ORIGIN = 0xC0000000, LENGTH = 32M
```

**Find SECTIONS and add before closing `}`**:
```ld
.sdram (NOLOAD) :
{
  . = ALIGN(4);
  _sdram_start = .;
  *(SORT(.sdram*))
  . = ALIGN(4);
  _sdram_end = .;
} > SDRAM AT > SDRAM
```

**Save file.**

---

## 3️⃣ Verify STMCubeMX (10 min)

Open: `UI_Designer/UI_Designer.ioc`

**Verify enabled** (should already be from CubeMX):
- ✅ FMC (SDRAM configured)
- ✅ LTDC (800×480 display)
- ✅ DMA2D (acceleration)
- ✅ GPIO (display pins)

**If any missing**: Generate missing peripheral in CubeMX

---

## 4️⃣ Build Project (5-30 min)

```bash
cd UI_Designer
make clean
make -j4
```

**Expected**: ✅ Build succeeds with no errors

**If errors**:
- "undefined reference to UI_Render" → Check .c files in Makefile
- Linker errors → Check SDRAM section in .ld file
- Other errors → See STM32_INTEGRATION_GUIDE.md

---

## 5️⃣ Flash & Test (5 min)

```bash
# With ST-Link connected and board powered
st-flash write build/UI_Designer.bin 0x08000000
```

**Expected**: 
- ✅ Flash succeeds
- ✅ Display shows rendered shapes/text
- ✅ Smooth at ~60 FPS

---

## 6️⃣ Design Your UI (Ongoing)

```bash
# From workspace root
python ui_builder.py

# In the GUI:
# 1. Create New Project
# 2. Draw rectangles, ovals, text
# 3. Click "Generate C Code"
# 4. Select UI_Designer directory
# 5. Files are generated/updated

# Back in IDE:
cd UI_Designer
make clean && make -j4
st-flash write build/UI_Designer.bin 0x08000000

# See your custom UI on display!
```

---

## 📚 Documentation

| For | Read This |
|-----|-----------|
| Full details | STM32_INTEGRATION_GUIDE.md |
| Step-by-step | INTEGRATION_CHECKLIST.md |
| Summary | INTEGRATION_SUMMARY.md |
| All files | FILE_MANIFEST.md |
| Code generation help | INTEGRATION_NOTES.md (auto-generated) |

---

## ✅ Verify It Works

Quick verification:
1. Display shows UI elements (rectangles, ovals, text)
2. No flickering or artifacts
3. ~60 FPS smooth updates

Run to check FPS:
```c
// Add to main loop temporarily:
printf("FPS: %lu\n", UI_GetFPS());
```

---

## 🆘 Quick Fixes

| Problem | Fix |
|---------|-----|
| Build fails | Add all .c files to Makefile |
| Blank display | Check SDRAM init, verify linker script |
| Slow (< 30 FPS) | Verify DMA2D enabled, check clock |
| Linker errors | Add SDRAM section to .ld file |

See **STM32_INTEGRATION_GUIDE.md** for full troubleshooting.

---

## 🎉 You're Done!

Your STM32H7 now renders amazing UIs at 60 FPS with hardware acceleration!

**Next**: Use ui_builder.py to design your own UI elements.

---

**Time invested: ~2-3 hours**  
**Time saved using this system: Days of driver coding!**

Happy building! 🚀
