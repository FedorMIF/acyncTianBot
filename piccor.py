from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageDraw, ImageFont
import asyncio

async def process_image(image_path: str, output_path: str, mode: str, enhancement_factor=None):
    image = Image.open(image_path)
    try:
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
    except:
        return(False)
    
    image.save(output_path)
    return(True)

async def add_demotivator_border(input_image_path: str, output_path: str, text):
    # Load the image
    image = Image.open(input_image_path)
    try:
        # Define the size of the borders and text band
        border_size = int(max(image.size) * 0.05)  # 5% of the image size
        bottom_band_height = int(border_size * 2)  # Twice the border size for the bottom band
        
        # Create a new image with border and bottom band
        new_width = image.width + border_size * 2
        new_height = image.height + border_size * 3
        bordered_image = Image.new('RGB', (new_width, new_height + bottom_band_height), 'black')
        
        # Paste the original image onto the bordered image
        bordered_image.paste(image, (border_size, border_size))
        
        # Add the text to the bottom band
        draw = ImageDraw.Draw(bordered_image)
        try:
            # Load a truetype or opentype font file, and create a font object.
            # This font file should be in the same directory as this script, or provide full path.
            font = ImageFont.truetype("arial.ttf", int(border_size * 0.75))
        except IOError:
            # If the custom font can't be loaded, we fall back to a default PIL font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        if len(text) > 1:
            text_length = (font.getlength(text + text[1]) - font.getlength(text[1])) #/ 64
        else:
            text_length = font.getlength(text) #/ 64  # Convert to pixels
        
        text_x = (new_width - text_length) // 2
        # Approximate the height by the font size as `getlength` does not provide height
        text_y = new_height + (bottom_band_height - int(border_size * 3)) // 2
        
        # Draw the text
        draw.text((text_x, text_y), text, font=font, fill="white")
        
        # Save or return the imagу
    except:
        return(False)
    
    bordered_image.save(output_path)
    return (True)
