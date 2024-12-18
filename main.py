import discord
from discord.ext import commands
from imageai.Detection import ObjectDetection
import cv2  # Optional for image processing

# Create an object detection instance
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("yolov3.pt")  # Replace with your model path
detector.loadModel()

# Configuración de Intents
intents = discord.Intents.default()
intents.message_content = True  # Para procesar contenido de mensajes
intents.messages = True  # Permite manejar mensajes (incluye adjuntos)

bot = commands.Bot(command_prefix='%', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Verificar si el mensaje tiene adjuntos
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                await message.channel.send(f'Se ha detectado una imagen subida: {attachment.url}')
    
    await bot.process_commands(message)
    
@bot.event
async def on_message(message):
    # ... (rest of your on_message function)

    if message.attachments:
        for attachment in message.attachments:
            # ... (download image)

            # Detect objects
            detections = detector.detectObjectsFromImage(input_image=image_path)

            # Process detections and create response message
            message = "Objetos detectados en la imagen:\n"
            if detections:
                for detection in detections:
                    message += f"- {detection['name']} ({detection['percentage_probability']:.2f}%)\n"
            else:
                message += "No se detectaron objetos."

            await message.channel.send(message)

            # ... (optional: clear downloaded image)

@bot.command()
async def hello(ctx):
    await ctx.send(f'¡Hola! Soy el bot {bot.user}!')

@bot.command()
async def heh(ctx, count_heh: int = 5):
    await ctx.send("he" * count_heh)

# Aquí puedes agregar tu token
bot.run("MTI0ODczMTU4NTc4NDg0NDM3OQ.GeZD5r.xdldHwQU2hFbBnTnYY4mwGXP-lSos1pAFQz9SY")
