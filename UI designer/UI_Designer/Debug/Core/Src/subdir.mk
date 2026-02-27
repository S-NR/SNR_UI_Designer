################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (14.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Src/adc.c \
../Core/Src/dac.c \
../Core/Src/dma2d.c \
../Core/Src/eth.c \
../Core/Src/fdcan.c \
../Core/Src/generated_ui.c \
../Core/Src/gpio.c \
../Core/Src/i2c.c \
../Core/Src/ltdc.c \
../Core/Src/main.c \
../Core/Src/octospi.c \
../Core/Src/sai.c \
../Core/Src/sdmmc.c \
../Core/Src/stm32h7xx_hal_msp.c \
../Core/Src/stm32h7xx_it.c \
../Core/Src/system_stm32h7xx.c \
../Core/Src/tim.c \
../Core/Src/ui_layout.c \
../Core/Src/ui_renderer.c \
../Core/Src/ui_renderer_stm.c \
../Core/Src/ui_stm_integration.c \
../Core/Src/usart.c \
../Core/Src/usb_otg.c 

C_DEPS += \
./Core/Src/adc.d \
./Core/Src/dac.d \
./Core/Src/dma2d.d \
./Core/Src/eth.d \
./Core/Src/fdcan.d \
./Core/Src/generated_ui.d \
./Core/Src/gpio.d \
./Core/Src/i2c.d \
./Core/Src/ltdc.d \
./Core/Src/main.d \
./Core/Src/octospi.d \
./Core/Src/sai.d \
./Core/Src/sdmmc.d \
./Core/Src/stm32h7xx_hal_msp.d \
./Core/Src/stm32h7xx_it.d \
./Core/Src/system_stm32h7xx.d \
./Core/Src/tim.d \
./Core/Src/ui_layout.d \
./Core/Src/ui_renderer.d \
./Core/Src/ui_renderer_stm.d \
./Core/Src/ui_stm_integration.d \
./Core/Src/usart.d \
./Core/Src/usb_otg.d 

OBJS += \
./Core/Src/adc.o \
./Core/Src/dac.o \
./Core/Src/dma2d.o \
./Core/Src/eth.o \
./Core/Src/fdcan.o \
./Core/Src/generated_ui.o \
./Core/Src/gpio.o \
./Core/Src/i2c.o \
./Core/Src/ltdc.o \
./Core/Src/main.o \
./Core/Src/octospi.o \
./Core/Src/sai.o \
./Core/Src/sdmmc.o \
./Core/Src/stm32h7xx_hal_msp.o \
./Core/Src/stm32h7xx_it.o \
./Core/Src/system_stm32h7xx.o \
./Core/Src/tim.o \
./Core/Src/ui_layout.o \
./Core/Src/ui_renderer.o \
./Core/Src/ui_renderer_stm.o \
./Core/Src/ui_stm_integration.o \
./Core/Src/usart.o \
./Core/Src/usb_otg.o 


# Each subdirectory must supply rules for building sources it contributes
Core/Src/%.o Core/Src/%.su Core/Src/%.cyclo: ../Core/Src/%.c Core/Src/subdir.mk
	$(error unable to generate command line)

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/adc.cyclo ./Core/Src/adc.d ./Core/Src/adc.o ./Core/Src/adc.su ./Core/Src/dac.cyclo ./Core/Src/dac.d ./Core/Src/dac.o ./Core/Src/dac.su ./Core/Src/dma2d.cyclo ./Core/Src/dma2d.d ./Core/Src/dma2d.o ./Core/Src/dma2d.su ./Core/Src/eth.cyclo ./Core/Src/eth.d ./Core/Src/eth.o ./Core/Src/eth.su ./Core/Src/fdcan.cyclo ./Core/Src/fdcan.d ./Core/Src/fdcan.o ./Core/Src/fdcan.su ./Core/Src/generated_ui.cyclo ./Core/Src/generated_ui.d ./Core/Src/generated_ui.o ./Core/Src/generated_ui.su ./Core/Src/gpio.cyclo ./Core/Src/gpio.d ./Core/Src/gpio.o ./Core/Src/gpio.su ./Core/Src/i2c.cyclo ./Core/Src/i2c.d ./Core/Src/i2c.o ./Core/Src/i2c.su ./Core/Src/ltdc.cyclo ./Core/Src/ltdc.d ./Core/Src/ltdc.o ./Core/Src/ltdc.su ./Core/Src/main.cyclo ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/octospi.cyclo ./Core/Src/octospi.d ./Core/Src/octospi.o ./Core/Src/octospi.su ./Core/Src/sai.cyclo ./Core/Src/sai.d ./Core/Src/sai.o ./Core/Src/sai.su ./Core/Src/sdmmc.cyclo ./Core/Src/sdmmc.d ./Core/Src/sdmmc.o ./Core/Src/sdmmc.su ./Core/Src/stm32h7xx_hal_msp.cyclo ./Core/Src/stm32h7xx_hal_msp.d ./Core/Src/stm32h7xx_hal_msp.o ./Core/Src/stm32h7xx_hal_msp.su ./Core/Src/stm32h7xx_it.cyclo ./Core/Src/stm32h7xx_it.d ./Core/Src/stm32h7xx_it.o ./Core/Src/stm32h7xx_it.su ./Core/Src/system_stm32h7xx.cyclo ./Core/Src/system_stm32h7xx.d ./Core/Src/system_stm32h7xx.o ./Core/Src/system_stm32h7xx.su ./Core/Src/tim.cyclo ./Core/Src/tim.d ./Core/Src/tim.o ./Core/Src/tim.su ./Core/Src/ui_layout.cyclo ./Core/Src/ui_layout.d ./Core/Src/ui_layout.o ./Core/Src/ui_layout.su ./Core/Src/ui_renderer.cyclo ./Core/Src/ui_renderer.d ./Core/Src/ui_renderer.o ./Core/Src/ui_renderer.su ./Core/Src/ui_renderer_stm.cyclo ./Core/Src/ui_renderer_stm.d ./Core/Src/ui_renderer_stm.o ./Core/Src/ui_renderer_stm.su ./Core/Src/ui_stm_integration.cyclo ./Core/Src/ui_stm_integration.d ./Core/Src/ui_stm_integration.o ./Core/Src/ui_stm_integration.su ./Core/Src/usart.cyclo ./Core/Src/usart.d ./Core/Src/usart.o ./Core/Src/usart.su ./Core/Src/usb_otg.cyclo ./Core/Src/usb_otg.d ./Core/Src/usb_otg.o ./Core/Src/usb_otg.su

.PHONY: clean-Core-2f-Src

