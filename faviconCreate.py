# Puedes usar este código en un script separado para crear un favicon básico
from PIL import Image, ImageDraw

# Crear una imagen 32x32
img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Dibujar un círculo azul
draw.ellipse([4, 4, 28, 28], fill='#3B82F6')

# Guardar como PNG
img.save('app/static/img/favicon.png')