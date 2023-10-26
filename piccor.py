from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import asyncio

async def process_image(image_path: str, output_path: str, mode: str, enhancement_factor=None):
    image = Image.open(image_path)
    
    if mode == 'bw':
        image = image.convert("L")
    elif mode == 'sepia':
        # Применение сепийного фильтра
        width, height = image.size
        pixels = image.load()  # создание матрицы пикселей

        for py in range(height):
            for px in range(width):
                r, g, b = image.getpixel((px, py))

                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                if tr > 255:
                    tr = 255

                if tg > 255:
                    tg = 255

                if tb > 255:
                    tb = 255

                pixels[px, py] = (tr,tg,tb)
    elif mode == 'sepiabw':
        image = image.convert("L")
        image = ImageOps.colorize(image, '#704214', '#C0A080')
    elif mode == 'blur':
        image = image.filter(ImageFilter.BLUR)
    elif mode == 'contour':
        image = image.filter(ImageFilter.CONTOUR)
    elif mode == 'detail':
        image = image.filter(ImageFilter.DETAIL)
    elif mode == 'emboss':
        image = image.filter(ImageFilter.EMBOSS)
    elif mode == 'sharpen':
        image = image.filter(ImageFilter.SHARPEN)
    elif mode == 'smooth':
        image = image.filter(ImageFilter.SMOOTH)
    elif mode == 'enhance':
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(enhancement_factor)
    
    image.save(output_path)

