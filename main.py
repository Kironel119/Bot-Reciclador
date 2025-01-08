import discord
from discord.ext import commands
from imageai.Detection import ObjectDetection
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configurar el detector de objetos
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("yolov3.pt")  # Cambia por tu modelo YOLOv3 descargado
detector.loadModel()

# Lista de reciclabilidad (puedes extenderla según sea necesario)
recyclability_index = {
    "bottle": 95,  # Botellas son muy reciclables
    "can": 90,     # Latas tienen alta reciclabilidad
    "plastic": 50, # Plástico tiene reciclabilidad moderada
    "paper": 80,   # Papel tiene buena reciclabilidad
    "bag": 40,     # Bolsas plásticas son difíciles de reciclar
    # Otros objetos...
}

# Configuración de Intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='%', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Procesar imágenes subidas
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                await message.channel.send(f'Se ha subido una imagen: {attachment.url}')

                # Descargar la imagen
                response = requests.get(attachment.url)
                image = Image.open(BytesIO(response.content))

                # Guardar temporalmente la imagen para detección
                input_path = "input_image.jpg"
                output_path = "output_image.jpg"
                image.save(input_path)

                # Detectar objetos en la imagen
                detections = detector.detectObjectsFromImage(
                    input_image=input_path,
                    output_image_path=output_path
                )

                # Calcular el índice de reciclabilidad
                total_recyclability = 0
                num_objects = 0
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("arial.ttf", size=24)

                for detection in detections:
                    name = detection['name']
                    recyclability = recyclability_index.get(name, 0)  # Índice de reciclabilidad
                    total_recyclability += recyclability
                    num_objects += 1

                    # Dibujar rectángulos y etiquetas
                    box_points = detection['box_points']
                    draw.rectangle(box_points, outline="green", width=3)
                    draw.text((box_points[0], box_points[1] - 30),
                              f"{name} ({recyclability}%)",
                              fill="green",
                              font=font)

                # Promedio de reciclabilidad
                avg_recyclability = (
                    total_recyclability / num_objects if num_objects > 0 else 0
                )
                avg_message = f"Reciclabilidad promedio: {avg_recyclability:.2f}%"

                # Guardar imagen procesada
                image.save(output_path)

                # Enviar el mensaje con reciclabilidad
                await message.channel.send(avg_message)

                # Enviar la imagen procesada
                with open(output_path, "rb") as output_file:
                    await message.channel.send(file=discord.File(output_file))

    # Procesar comandos del bot
    await bot.process_commands(message)

# Comando de ejemplo
@bot.command()
async def hello(ctx):
    await ctx.send(f'¡Hola! Soy el bot {bot.user}!')

@bot.command()
async def heh(ctx, count_heh: int = 5):
    await ctx.send("he" * count_heh)
    
@bot.command()
async def What_are_you_doing(ctx):
    await ctx.send(f'Soy el bot {bot.user} que te mustra que cosas se pueden reciclar de una imagen!')

# Coloca aquí tu token
bot.run('MTI1NzQxMTAyMDc4ODYwMDkzNg.G4Lj2A.MqBWB9ApiZvSiGdfkhrpu1OHgAbSZ_oQe_7tGY')
