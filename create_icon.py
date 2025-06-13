from PIL import Image, ImageDraw

# Create a new image with a white background
size = (256, 256)
image = Image.new('RGB', size, 'white')
draw = ImageDraw.Draw(image)

# Draw a mouse cursor shape
# Base
draw.rectangle([(50, 50), (206, 206)], fill='#007bff')
# Pointer
draw.polygon([(206, 50), (256, 0), (206, 100)], fill='#0056b3')

# Save as ICO
image.save('icon.ico', format='ICO', sizes=[(256, 256)]) 