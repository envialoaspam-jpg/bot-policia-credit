import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Frases de la Policía del Credit desmintiendo directamente a la persona y la coaster
FRASES_RESPUESTA = [
    # --- Modificadas de la tanda anterior (adaptadas a respuesta directa) ---
    "Qué va, mentira. Qué se va a haber subido ahí, si lo más lejos que ha ido es a Cuca Park.",
    "Ni de coña. Tú no te creas nada, que a esa atracción no se ha subido ni en sueños.",
    "Falso total. A Cuca de Cuca Park le encantan sus mentiras.",
    "Para nada. Ese no ha visto una RMC ni en foto.",
    "Mentira. Lo más extremo a lo que ha aspirado en su vida es a la montaña rusa de Peppa Pig.",
    "Qué va. Su mayor hito coastero fue no marearse en las tazas de la feria.",
    "Imposible. Se marea hasta subiendo en ascensor y quiere colarnos que ha subido a eso.",
    "Mentira rotunda. Le da miedo la sombra del Coaster-Express y viene aquí de experto.",
    "Qué va a haber subido. Si le quitas la feria de su pueblo se queda en 0 credits reales.",
    "Fake total. Fantasma nivel: poner en el recuento los vídeos que ve en YouTube.",
    "Ni hablar. A ese le pones un airtime enfrente y llama a su madre llorando.",
    "Para nada. Ese credit tiene menos validez que un billete del Monopoly.",
    "Mentira de manual. Su lista de credits es más inventada que una peli de ciencia ficción.",
    "Qué va. Lo más cerca que ha estado de esa coaster es vendiendo palomitas en la puerta del parque.",
    "Imposible. Se cree que cuenta como credit haberse hecho una foto delante de la vía.",
    "Qué va a haber subido. Le dan escalofríos los toboganes de agua pequeños y me viene con estas.",
    "Mentira. Ese no aguantaría ni el frenado final de esa bestia sin pedir auxilio.",
    "Para nada. Puso un pie en la cola, vio el peralte y se volvió para el coche.",
    "Fake absoluto. Su historial de credits es 90% fantasía y 10% parque infantil.",
    "Qué va, mentira. Que deje de inventar, que sabemos que se quedó cuidando las mochilas abajo.",
    "Ni de coña. Si le miden la altura en la entrada de esa coaster lo mandan directo a párvulos.",
    "Imposible. Decir que ha subido ahí es como decir que ha pisado la Luna.",
    "Qué va. Se montó en el tren parado en la estación para la foto y ya se cree que la ha vivido.",
    "Mentira cochina. Ese credit caducó antes de que tuviera valor legal.",
    "Para nada. A ese le quitan los Powered Coasters y se queda sin expediente.",
    "Fake total. Ni con un pase VIP inventado entraría esa mentira en el recuento.",
    "Qué va. Está a un paso de contar las escaleras mecánicas como roller coaster.",
    "Mentira. Su mayor subidón de adrenalina ha sido cruzarse un semáforo en ámbar.",
    "Ni hablar. Le enseñas un loop de esa atracción y se persigna.",
    "Para nada. Eso no es un credit, es un delirio de grandeza.",
    "Qué va. Cree que por ver el POV tres veces en TikTok ya cuenta como subido.",
    "Imposible. Se mareó en el tren de la bruja y quiere convencernos de que ha probado eso.",
    "Mentira rotunda. Si la Policía del Credit pusiera multas de verdad, estaría en la cárcel.",
    "Qué va a haber subido. Ha ido más veces al baño del parque que a las atracciones de verdad.",
    "Fake. El único credit que tiene verificado es el de la catapulta... y en simulación.",
    "Ni de coña. Ese no ha sentido un launch en su vida, solo el susto al ver la cuenta.",
    "Mentira de las gordas. Miente mejor que habla. Credit totalmente DENEGADO.",
    "Para nada. Dile que enseñe la foto On-Ride o que se vuelva por donde ha venido.",
    "Qué va. Ese credit es más falso que un euro de madera.",
    "Imposible. Le temblaron las piernas en la cola express y dice que repetirá.",
    "Mentira. Se piensa que un alpine coaster en la sierra cuenta como mega coaster.",
    "Qué va. A ese lo subes a un launch de esos y se le desconfigura la cara.",
    "Para nada. Tiene el certificado de fantasma de oro por la Policía del Credit.",
    "Fake absoluto. Que deje de sumar en su cabeza, que el recuento real da pena.",
    "Qué va a haber subido. Vio la primera bajada desde abajo y dijo 'hoy no me apetece'.",
    "Mentira. Su concepto de 'montaña rusa intensa' es la alfombra mágica del circo.",
    "Ni hablar. Ese no aguanta ni 2G de fuerza sin pedir la baja médica.",
    "Imposible. Le da miedo la velocidad de un patinete eléctrico y mira con qué nos sale.",
    "Qué va. Cero pruebas, cero dudas: esa historia es un invento gigantesco.",
    "Caso cerrado: no ha pisado esa vía ni de transeúnte.",

    # --- Tanda adaptada con referencias populares y locales ---
    "Qué va, mentira. Es más fantasma que Bollino, a ese no se lo cree ni su abuela.",
    "Para nada. Esto con la tita Merche no pasaba. Menuda fantasmada se acaba de marcar.",
    "Qué va, mentira. No se ha subido ahí, si lo más lejos que ha ido es al Carrefour de la esquina.",
    "Ni de coña. A la tita Merche le daría un apuro ver cómo miente sobre sus credits.",
    "Mentira total. Es más cuento que los hermanos Grimm y más fantasma que Bollino juntos.",
    "Qué va. Le pones un peralte enfrente y sale corriendo a llamar a la tita Merche.",
    "Cero pruebas y cien por ciento de película. A Cuca de Cuca Park le encantan sus mentiras.",

    # --- Tanda adaptada con Parques Nacionales ---
    "Qué va a haber subido a eso... Si en Shambhala se quedó abajo cuidando las mochilas.",
    "Mentira. Lo más fuerte que ha probado es el Stampida y salió pidiendo la baja por latigazo.",
    "Imposible. Decir que se ha subido ahí es como decir que Furius Baco arranca suave.",
    "Qué va. Se mareó en las tazas de la Warner y nos quiere vender esa milonga.",
    "Ni en sueños. Con suerte ha ido a Terra Mítica y le dio miedo el Titánide.",
    "Mentira rotunda. Su mayor hito fue armarse de valor para subir a la Abismo en Madrid.",
    "Para nada. Se piensa que subir al Tren de la Mina de PortAventura lo convierte en experto.",
    "Qué va. Se subió al Coaster-Express, gritó como si no hubiera un mañana y no ha vuelto a pisar un parque.",

    # --- Tanda adaptada con Parques e Coasters Internacionales ---
    "Mentira total. Ese no ha visto una RMC ni en foto de portada.",
    "¿Subirse a eso? Si en Zadra de Energylandia se desmaya solo de ver el drop desde el parking.",
    "Qué va. Dice que probó Toutatis en Parc Astérix, pero seguro que se quedó en la tienda de recuerdos.",
    "Imposible. ¿Voltron en Europa-Park? Si le metes un launch helicoidal y sale pidiendo confesión.",
    "Para nada. Lo pones en la cola de Taron en Phantasialand y se da la vuelta antes del pre-show.",
    "Mentira. En Efteling ya se asustó con los árboles parlantes del Bosque de Cuentos.",
    "Qué va. Decir que ha volado a Reino Unido para probar Nemesis Reborn... ni en sus mejores sueños.",
    "Fake total. Cree que por ver el POV en YouTube de Kingda Ka ya cuenta como credit verificado.",
    "Qué va a haber subido. Ese credit en una RMC tiene menos validez que un billete de tres euros.",
    "Ni de coña. Le dices que Hyperia tiene airtime negativo y busca un refugio nuclear."
]

async def enviar_pregunta_inicial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = "Dime a quién quieres que investigue y si el credit que dice es lícito."
    if update.message:
        await update.message.reply_text(mensaje)
    elif update.callback_query:
        await update.callback_query.message.reply_text(mensaje)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_pregunta_inicial(update, context)

async def responder_e_investigar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    frase = random.choice(FRASES_RESPUESTA)
    keyboard = [
        [InlineKeyboardButton("🔍 Investigar a otra persona", callback_data="investigar_otro")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(frase, reply_markup=reply_markup)

async def boton_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "investigar_otro":
        await enviar_pregunta_inicial(update, context)

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("No se ha encontrado la variable BOT_TOKEN.")
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_e_investigar))
    app.add_handler(CallbackQueryHandler(boton_callback))
    
    print("Policía del Credit online y patrullando...")
    app.run_polling()
