from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageDraw, ImageFont, __version__
def add_demotivator_border(input_image_path: str, output_path: str, text):
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
            text_length = (font.getlength(text + text[1]) - font.getlength(text[1]))
            print(text_length, 1)
        else:
            text_length = font.getlength(text)  # Convert to pixels
            print(text_length, 2)

        print(new_width)
        
        text_x = (new_width - text_length) // 2
        print(text_x)
        # Approximate the height by the font size as `getlength` does not provide height
        text_y = new_height + (bottom_band_height - int(border_size)*3) // 2

    
        # Draw the text
        draw.text((text_x, text_y), text, font=font, fill="white")
        
        # Save or return the imagу
    except Exception as e:
        print(e)
        return(False)
    
    bordered_image.save(output_path)
    return (True)


if not add_demotivator_border('input_image_dem.jpg', 'image_dem.png', 'jdjfdhgfdhgfdgfj'):
    print(__version__)