"""
seed_lessons.py — Contenido educativo financiero para Investi AI
Ejecutar una vez para poblar la base de datos con módulos, lecciones, quizzes y logros.

Orden pedagógico:
1. Finanzas personales y presupuesto (la base de todo)
2. Ahorro inteligente
3. Deuda y crédito
4. Interés compuesto y el valor del dinero en el tiempo
5. Inversión básica (acciones, fondos, ETFs)
"""
from sqlalchemy.orm import Session
from models_education import (
    EducationModule, Lesson, QuizQuestion, Achievement
)

# ═══════════════════════════════════════════════════════════════════════════════
#  MÓDULOS
# ═══════════════════════════════════════════════════════════════════════════════

MODULES = [
    {
        "slug": "finanzas-personales",
        "title": "Finanzas Personales y Presupuesto",
        "description": "Aprende a organizar tu dinero, crear un presupuesto que funcione y tomar el control de tus finanzas desde hoy.",
        "icon": "💰",
        "order": 1,
    },
    {
        "slug": "ahorro-inteligente",
        "title": "Ahorro Inteligente",
        "description": "Descubre estrategias para ahorrar sin sufrir, crear tu fondo de emergencia y hacer que tu dinero trabaje para ti.",
        "icon": "🐷",
        "order": 2,
    },
    {
        "slug": "deuda-y-credito",
        "title": "Deuda y Crédito",
        "description": "Entiende cómo funciona la deuda, cuándo es buena o mala, y cómo usar el crédito a tu favor sin caer en trampas.",
        "icon": "💳",
        "order": 3,
    },
    {
        "slug": "interes-compuesto",
        "title": "Interés Compuesto y el Valor del Dinero",
        "description": "El superpoder financiero más grande del mundo. Aprende cómo el tiempo multiplica tu dinero de forma exponencial.",
        "icon": "📈",
        "order": 4,
    },
    {
        "slug": "inversion-basica",
        "title": "Inversión Básica",
        "description": "Tu primer paso en el mundo de las inversiones: acciones, fondos, ETFs y cómo construir tu portafolio.",
        "icon": "🚀",
        "order": 5,
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
#  LECCIONES + QUIZZES
# ═══════════════════════════════════════════════════════════════════════════════

LESSONS = {
    # ─── MÓDULO 1: Finanzas Personales ─────────────────────────────────────
    "finanzas-personales": [
        {
            "slug": "que-son-las-finanzas-personales",
            "title": "¿Qué son las finanzas personales?",
            "summary": "Tu dinero, tus reglas. Aprende por qué manejar tu plata es la habilidad más importante que nadie te enseñó en el colegio.",
            "content": """# ¿Qué son las finanzas personales?

Imagina que tu dinero es como el agua: si no la diriges, se escapa por todas partes. Las finanzas personales son simplemente **el arte de dirigir tu dinero hacia donde TÚ quieres**.

## ¿Por qué importa?

No importa si ganas mucho o poco. Lo que importa es **qué haces con lo que ganas**. Hay personas que ganan millones y terminan en quiebra, y personas con ingresos modestos que construyen patrimonio.

## Los 3 pilares de las finanzas personales

### 1. Ganar 💪
Tu ingreso es tu herramienta principal. Puede venir de tu trabajo, un negocio, freelance o inversiones.

### 2. Administrar 🧠
Aquí es donde la magia ocurre. Saber a dónde va cada peso te da poder sobre tu futuro.

### 3. Hacer crecer 🌱
Una vez que controlas tus gastos, puedes poner tu dinero a trabajar para ti a través del ahorro y la inversión.

## El error más común

La mayoría de personas vive en piloto automático financiero: ganan, gastan, y repiten. Sin un plan, el dinero simplemente desaparece.

> **La buena noticia:** No necesitas ser experto en matemáticas. Solo necesitas un sistema simple y la disciplina para seguirlo.""",
            "fun_fact": "El 78% de las personas que llevan un presupuesto reportan sentirse menos estresadas con el dinero. ¡Tu mente te lo agradecerá!",
            "difficulty": 1,
            "xp_reward": 50,
            "order": 1,
            "quiz": [
                {
                    "question": "¿Cuáles son los 3 pilares de las finanzas personales?",
                    "option_a": "Ganar, gastar, pedir prestado",
                    "option_b": "Ganar, administrar, hacer crecer",
                    "option_c": "Ahorrar, invertir, jubilarse",
                    "option_d": "Trabajar, descansar, repetir",
                    "correct_option": "b",
                    "explanation": "Los 3 pilares son: Ganar (tu ingreso), Administrar (controlar gastos) y Hacer crecer (ahorro e inversión). No basta con ganar, hay que saber dirigir el dinero.",
                    "order": 1,
                },
                {
                    "question": "¿Qué es más importante para tus finanzas?",
                    "option_a": "Cuánto ganas",
                    "option_b": "Qué haces con lo que ganas",
                    "option_c": "En qué banco tienes tu cuenta",
                    "option_d": "Cuántas tarjetas de crédito tienes",
                    "correct_option": "b",
                    "explanation": "Lo que haces con tu dinero importa más que cuánto ganas. Muchas personas con altos ingresos terminan endeudadas por no administrar bien.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es el error financiero más común según la lección?",
                    "option_a": "No tener tarjeta de crédito",
                    "option_b": "Vivir en piloto automático financiero",
                    "option_c": "Invertir demasiado pronto",
                    "correct_option": "b",
                    "explanation": "Vivir en piloto automático (ganar, gastar, repetir sin un plan) es el error más común. Sin un sistema, el dinero simplemente desaparece.",
                    "order": 3,
                },
            ],
        },
        {
            "slug": "crea-tu-primer-presupuesto",
            "title": "Crea tu primer presupuesto",
            "summary": "La regla 50/30/20 y cómo aplicarla sin volverte loco. Tu primer paso hacia la libertad financiera.",
            "content": """# Crea tu primer presupuesto

Un presupuesto no es una cárcel para tu dinero — es un **mapa** que te muestra a dónde va y te ayuda a decidir a dónde QUIERES que vaya.

## La Regla 50/30/20

Esta es la fórmula más simple y efectiva para empezar:

### 50% — Necesidades 🏠
Lo esencial para vivir:
- Arriendo o hipoteca
- Servicios (agua, luz, internet)
- Alimentación básica
- Transporte al trabajo
- Salud

### 30% — Deseos 🎮
Lo que hace la vida divertida:
- Entretenimiento y streaming
- Restaurantes y salidas
- Ropa no esencial
- Hobbies
- Viajes

### 20% — Futuro 🚀
Tu yo del futuro te lo agradecerá:
- Ahorro (fondo de emergencia)
- Pago extra de deudas
- Inversiones

## Ejemplo práctico

Si ganas $3,000,000 COP al mes:
- **$1,500,000** → Necesidades
- **$900,000** → Deseos
- **$600,000** → Ahorro e inversión

## Consejos para que funcione

1. **Registra TODO durante 1 mes** — Así descubres tu realidad
2. **Usa categorías simples** — No te compliques con 50 categorías
3. **Revísalo cada semana** — 10 minutos bastan
4. **Ajusta sin culpa** — Un presupuesto es flexible, no perfecto""",
            "fun_fact": "La regla 50/30/20 fue popularizada por Elizabeth Warren (sí, la senadora de EE.UU.) cuando era profesora de Harvard. ¡Hasta los políticos saben de presupuestos!",
            "difficulty": 1,
            "xp_reward": 60,
            "order": 2,
            "quiz": [
                {
                    "question": "Según la regla 50/30/20, ¿qué porcentaje debería ir a necesidades?",
                    "option_a": "20%",
                    "option_b": "30%",
                    "option_c": "50%",
                    "option_d": "60%",
                    "correct_option": "c",
                    "explanation": "El 50% de tus ingresos debería cubrir necesidades esenciales como vivienda, alimentación, servicios y transporte.",
                    "order": 1,
                },
                {
                    "question": "Si ganas $2,000,000 COP al mes, ¿cuánto deberías destinar al ahorro según la regla 50/30/20?",
                    "option_a": "$200,000",
                    "option_b": "$400,000",
                    "option_c": "$600,000",
                    "option_d": "$1,000,000",
                    "correct_option": "b",
                    "explanation": "El 20% de $2,000,000 = $400,000 para ahorro e inversión. Este es tu mínimo recomendado para construir tu futuro financiero.",
                    "order": 2,
                },
                {
                    "question": "¿Qué NO es un consejo dado en la lección para mantener tu presupuesto?",
                    "option_a": "Registra todo durante 1 mes",
                    "option_b": "Nunca ajustes tu presupuesto",
                    "option_c": "Revísalo cada semana",
                    "correct_option": "b",
                    "explanation": "La lección dice que un presupuesto es flexible, no perfecto. Ajustarlo sin culpa es parte del proceso.",
                    "order": 3,
                },
            ],
        },
        {
            "slug": "gastos-hormiga",
            "title": "Los gastos hormiga: el enemigo invisible",
            "summary": "Esos pequeños gastos diarios que parecen inofensivos pero te cuestan millones al año. Aprende a detectarlos.",
            "content": """# Los gastos hormiga: el enemigo invisible

¿Alguna vez llegaste a fin de mes pensando "¿a dónde se fue mi plata"? Probablemente fueron los **gastos hormiga** — pequeños gastos que parecen insignificantes pero se acumulan de forma brutal.

## ¿Qué son los gastos hormiga? 🐜

Son compras pequeñas y frecuentes que haces casi sin pensar:
- El café de $8,000 diario
- Snacks en la tienda
- Suscripciones que no usas
- Domicilios por pereza de cocinar
- Compras impulsivas online

## Hagamos las cuentas 🔢

Un café diario de $8,000:
- **Semanal:** $56,000
- **Mensual:** $240,000
- **Anual:** $2,880,000

¡Casi **3 millones de pesos** en café! Y eso es solo un gasto hormiga. Ahora suma todos los demás.

## El truco de las 24 horas ⏰

Antes de cualquier compra no esencial, espera 24 horas. Si al día siguiente todavía la quieres, cómprala. Vas a descubrir que el 70% de las veces, ya no la necesitas.

## No se trata de no gastar

No estamos diciendo que nunca tomes café. Se trata de ser **consciente** de tus gastos. La diferencia entre ser rico y ser pobre muchas veces no está en el ingreso, sino en los miles de pequeñas decisiones diarias.

## Plan de acción

1. **Revisa tus extractos bancarios** del último mes
2. **Marca con rojo** todo gasto que no fue esencial
3. **Suma el total** — te vas a sorprender
4. **Elige 2 o 3** gastos hormiga para eliminar o reducir
5. **Redirige ese dinero** a tu ahorro""",
            "fun_fact": "Un estudio encontró que el colombiano promedio gasta alrededor de $500,000 al mes en gastos hormiga. ¡Eso son $6 millones al año que podrían estar generando rendimientos!",
            "difficulty": 1,
            "xp_reward": 50,
            "order": 3,
            "quiz": [
                {
                    "question": "¿Cuánto cuesta al año un gasto hormiga de $8,000 diarios?",
                    "option_a": "$960,000",
                    "option_b": "$1,920,000",
                    "option_c": "$2,880,000",
                    "option_d": "$3,600,000",
                    "correct_option": "c",
                    "explanation": "$8,000 × 30 días = $240,000 mensual. $240,000 × 12 meses = $2,880,000 al año. Los pequeños gastos se convierten en grandes sumas.",
                    "order": 1,
                },
                {
                    "question": "¿En qué consiste el 'truco de las 24 horas'?",
                    "option_a": "Ahorrar todo lo que ganas en 24 horas",
                    "option_b": "Esperar 24 horas antes de hacer una compra no esencial",
                    "option_c": "Revisar tu cuenta bancaria cada 24 horas",
                    "correct_option": "b",
                    "explanation": "El truco es esperar 24 horas antes de comprar algo no esencial. La mayoría de veces descubres que ya no lo necesitas.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es el mensaje principal sobre los gastos hormiga?",
                    "option_a": "Nunca debes gastar en cosas pequeñas",
                    "option_b": "Ser consciente de tus pequeños gastos diarios",
                    "option_c": "Solo comprar con tarjeta de crédito",
                    "correct_option": "b",
                    "explanation": "No se trata de nunca gastar, sino de ser consciente. Las pequeñas decisiones diarias hacen una gran diferencia a largo plazo.",
                    "order": 3,
                },
            ],
        },
    ],

    # ─── MÓDULO 2: Ahorro Inteligente ──────────────────────────────────────
    "ahorro-inteligente": [
        {
            "slug": "pagate-a-ti-primero",
            "title": "Págate a ti primero",
            "summary": "El secreto #1 de las personas que logran ahorrar: no esperes a que sobre, sepáralo antes.",
            "content": """# Págate a ti primero

Este es probablemente el consejo financiero más poderoso que existe, y cabe en una frase: **Antes de pagar cualquier cosa, págate a ti mismo.**

## ¿Qué significa?

La mayoría de personas:
1. Reciben su sueldo
2. Pagan cuentas y gastos
3. Intentan ahorrar "lo que sobra"
4. Spoiler: nunca sobra nada 😅

Las personas financieramente exitosas:
1. Reciben su sueldo
2. **Separan su ahorro PRIMERO**
3. Pagan cuentas y gastos con lo que queda
4. Se adaptan al presupuesto restante

## ¿Por qué funciona?

Es psicología pura. Cuando el dinero está en tu cuenta, siempre encuentras algo en qué gastarlo. Pero si lo separas automáticamente, **tu cerebro se adapta** a vivir con menos sin sentir la diferencia.

## Cómo implementarlo

### Paso 1: Define tu porcentaje
Empieza con lo que puedas. Incluso un 5% es mejor que nada. Lo ideal es llegar al 20%.

### Paso 2: Automatiza
Configura una transferencia automática el mismo día que recibes tu pago. A otra cuenta que NO tenga tarjeta débito.

### Paso 3: Olvídate
Actúa como si ese dinero no existiera. Tu presupuesto mensual es tu ingreso MENOS tu ahorro automático.

## El efecto bola de nieve

- Mes 1 al 3: "Esto es difícil, siento que me falta plata"
- Mes 4 al 6: "Ya me acostumbré, ni lo noto"
- Mes 7 al 12: "¡Tengo ahorros por primera vez en mi vida!"
- Año 2+: "¿Cómo vivía sin hacer esto?"

> **Regla de oro:** Si esperas a que sobre para ahorrar, nunca vas a ahorrar.""",
            "fun_fact": "Este concepto viene del libro 'El Hombre Más Rico de Babilonia' escrito en 1926. Casi 100 años después, sigue siendo el consejo financiero #1.",
            "difficulty": 1,
            "xp_reward": 60,
            "order": 1,
            "quiz": [
                {
                    "question": "¿Qué significa 'pagarte a ti primero'?",
                    "option_a": "Comprarte algo bonito cada mes",
                    "option_b": "Separar tu ahorro ANTES de pagar gastos",
                    "option_c": "Pagar tus deudas antes que todo",
                    "correct_option": "b",
                    "explanation": "Pagarte a ti primero significa separar tu ahorro automáticamente antes de pagar cualquier otra cosa. Así garantizas que siempre ahorras.",
                    "order": 1,
                },
                {
                    "question": "¿Por qué es importante automatizar el ahorro?",
                    "option_a": "Para ganar más intereses",
                    "option_b": "Porque tu cerebro se adapta a vivir con lo que queda",
                    "option_c": "Para evitar pagar impuestos",
                    "correct_option": "b",
                    "explanation": "Cuando automatizas, tu cerebro se adapta a vivir con el dinero restante sin sentir que te falta. Es pura psicología a tu favor.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es el porcentaje mínimo sugerido para empezar a ahorrar?",
                    "option_a": "1%",
                    "option_b": "5%",
                    "option_c": "20%",
                    "option_d": "50%",
                    "correct_option": "b",
                    "explanation": "La lección sugiere empezar con lo que puedas, incluso un 5%. Lo ideal es llegar al 20%, pero lo importante es empezar.",
                    "order": 3,
                },
            ],
        },
        {
            "slug": "fondo-de-emergencia",
            "title": "Tu fondo de emergencia",
            "summary": "La red de seguridad que te salva de las deudas cuando la vida te sorprende. ¿Cuánto necesitas?",
            "content": """# Tu fondo de emergencia

La vida es impredecible. Se te daña el carro, te enfermas, pierdes el empleo. Sin un fondo de emergencia, estas situaciones te empujan directo a las deudas.

## ¿Qué es un fondo de emergencia?

Es dinero guardado EXCLUSIVAMENTE para emergencias reales. No es para vacaciones, no es para el Black Friday, no es para "oportunidades".

### ¿Qué SÍ es una emergencia?
- Pérdida de empleo
- Emergencia médica
- Reparación urgente del hogar o vehículo
- Gastos inesperados críticos

### ¿Qué NO es una emergencia?
- Descuentos o promociones
- Un viaje de último minuto
- Antojos o compras impulsivas

## ¿Cuánto necesitas?

La regla general:

| Situación | Meses de gastos |
|-----------|----------------|
| Empleo estable, sin dependientes | 3 meses |
| Empleo estable, con familia | 6 meses |
| Freelancer o ingreso variable | 6-9 meses |
| Emprendedor | 9-12 meses |

### Ejemplo
Si tus gastos mensuales son $2,500,000 COP y eres empleado con familia, necesitas: $2,500,000 × 6 = **$15,000,000 COP**

## ¿Dónde guardarlo?

Tu fondo debe ser:
- **Líquido** — Que puedas sacarlo rápido
- **Seguro** — Sin riesgo de perderlo
- **Separado** — En una cuenta diferente a la de uso diario

Opciones recomendadas: cuenta de ahorros de alto rendimiento, CDT a corto plazo, o fondos de inversión de bajo riesgo.

## Plan paso a paso

1. Calcula tus gastos mensuales esenciales
2. Multiplica por los meses que necesitas
3. Divide esa meta en metas mensuales pequeñas
4. Automatiza un aporte mensual
5. ¡Celebra cada milestone!""",
            "fun_fact": "Según encuestas, el 60% de los latinoamericanos no podría cubrir un gasto inesperado de $1,000,000 COP sin endeudarse. ¡Tener un fondo de emergencia te pone en el top 40%!",
            "difficulty": 1,
            "xp_reward": 60,
            "order": 2,
            "quiz": [
                {
                    "question": "¿Para qué sirve un fondo de emergencia?",
                    "option_a": "Para aprovechar ofertas y descuentos",
                    "option_b": "Para cubrir gastos inesperados y urgentes",
                    "option_c": "Para invertir en la bolsa de valores",
                    "correct_option": "b",
                    "explanation": "El fondo de emergencia es exclusivamente para emergencias reales como pérdida de empleo, emergencias médicas o reparaciones urgentes.",
                    "order": 1,
                },
                {
                    "question": "Si eres empleado con familia y gastas $3,000,000 al mes, ¿cuánto debería ser tu fondo de emergencia?",
                    "option_a": "$9,000,000",
                    "option_b": "$18,000,000",
                    "option_c": "$36,000,000",
                    "correct_option": "b",
                    "explanation": "Con empleo estable y familia, necesitas 6 meses de gastos. $3,000,000 × 6 = $18,000,000.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál de estas características debe tener tu fondo de emergencia?",
                    "option_a": "Alto rendimiento, aunque sea riesgoso",
                    "option_b": "Líquido, seguro y separado de tu cuenta diaria",
                    "option_c": "Invertido en acciones para que crezca rápido",
                    "correct_option": "b",
                    "explanation": "Tu fondo debe ser líquido (accesible rápido), seguro (sin riesgo) y separado (para no tentarte a gastarlo).",
                    "order": 3,
                },
            ],
        },
    ],

    # ─── MÓDULO 3: Deuda y Crédito ─────────────────────────────────────────
    "deuda-y-credito": [
        {
            "slug": "deuda-buena-vs-mala",
            "title": "Deuda buena vs. deuda mala",
            "summary": "No toda deuda es mala. Aprende a diferenciar la que te construye de la que te destruye.",
            "content": """# Deuda buena vs. deuda mala

Muchas personas piensan que TODA deuda es mala. Otros usan la deuda sin pensar. La verdad está en el medio: **hay deuda que te construye y deuda que te destruye.**

## Deuda buena ✅

Es la que **pone dinero en tu bolsillo** a largo plazo o te ayuda a generar más valor:

- **Educación** — Un pregrado o maestría que aumenta tu ingreso
- **Vivienda** — Una hipoteca para tu casa (el bien se valoriza)
- **Negocio** — Un préstamo para crear o expandir un negocio rentable

### Características de la deuda buena:
- Tasa de interés baja
- Genera retorno a futuro
- Tiene un plan de pago claro
- Financia un activo (algo que sube de valor)

## Deuda mala ❌

Es la que **saca dinero de tu bolsillo** y financia cosas que pierden valor:

- **Tarjeta de crédito al máximo** para compras impulsivas
- **Préstamos para vacaciones** o lujos
- **Financiar el último celular** a 36 cuotas con interés alto
- **Gota a gota** — NUNCA. Las tasas son abusivas.

### Características de la deuda mala:
- Tasa de interés alta
- Financia consumo (cosas que pierden valor)
- No tiene plan de pago realista
- Te genera estrés financiero

## La regla del 30%

Tu total de pagos de deuda mensual NO debería superar el 30% de tus ingresos. Si estás por encima, estás en zona de peligro.

Ejemplo: Si ganas $4,000,000, tus cuotas de deuda no deberían sumar más de $1,200,000 al mes.

## Antes de endeudarte, pregúntate:

1. ¿Esto va a generar más dinero o valor a futuro?
2. ¿Puedo pagar las cuotas sin comprometer mis necesidades básicas?
3. ¿La tasa de interés es razonable?
4. ¿Tengo un plan claro para pagar esto?

Si alguna respuesta es NO, probablemente es deuda mala.""",
            "fun_fact": "Warren Buffett, uno de los hombres más ricos del mundo, todavía vive en la casa que compró en 1958 por $31,500. Él dice que la deuda más peligrosa es la del consumo impulsivo.",
            "difficulty": 1,
            "xp_reward": 60,
            "order": 1,
            "quiz": [
                {
                    "question": "¿Cuál de estos es un ejemplo de deuda BUENA?",
                    "option_a": "Financiar unas vacaciones con tarjeta de crédito",
                    "option_b": "Un préstamo educativo para una maestría",
                    "option_c": "Comprar el último celular a 36 cuotas",
                    "correct_option": "b",
                    "explanation": "Un préstamo educativo es deuda buena porque aumenta tu capacidad de generar ingresos a futuro. Financia un 'activo' (tu conocimiento).",
                    "order": 1,
                },
                {
                    "question": "¿Qué porcentaje máximo de tus ingresos deberían representar tus pagos de deuda?",
                    "option_a": "10%",
                    "option_b": "30%",
                    "option_c": "50%",
                    "option_d": "70%",
                    "correct_option": "b",
                    "explanation": "La regla del 30% dice que tus pagos mensuales de deuda no deben superar el 30% de tus ingresos para mantener finanzas saludables.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es la característica principal de la deuda buena?",
                    "option_a": "Tiene cuotas pequeñas",
                    "option_b": "Genera retorno o valor a futuro",
                    "option_c": "Es aprobada rápidamente",
                    "correct_option": "b",
                    "explanation": "La deuda buena financia activos o situaciones que generan más valor o ingreso a futuro, como educación, vivienda o un negocio.",
                    "order": 3,
                },
            ],
        },
    ],

    # ─── MÓDULO 4: Interés Compuesto ───────────────────────────────────────
    "interes-compuesto": [
        {
            "slug": "la-octava-maravilla",
            "title": "La octava maravilla del mundo",
            "summary": "Einstein supuestamente dijo que el interés compuesto es la fuerza más poderosa del universo. Descubre por qué.",
            "content": """# La octava maravilla del mundo

> "El interés compuesto es la octava maravilla del mundo. Quien lo entiende, lo gana. Quien no, lo paga." — Atribuido a Albert Einstein

## Interés simple vs. interés compuesto

### Interés Simple
Ganas intereses solo sobre tu dinero inicial.

Ejemplo: $1,000,000 al 10% anual simple durante 10 años
- Cada año ganas $100,000
- Después de 10 años: $2,000,000

### Interés Compuesto 🚀
Ganas intereses sobre tu dinero inicial **Y sobre los intereses que ya ganaste**.

Ejemplo: $1,000,000 al 10% anual compuesto durante 10 años
- Año 1: $1,100,000
- Año 2: $1,210,000 (el 10% se calcula sobre $1,100,000)
- Año 5: $1,610,510
- Año 10: **$2,593,742**

¡$593,742 más que con interés simple! Y la diferencia crece exponencialmente con el tiempo.

## La magia del tiempo ⏳

El interés compuesto tiene un mejor amigo: **el tiempo**. Mira la diferencia:

$500,000 mensuales al 10% anual:
- **10 años:** $102 millones
- **20 años:** $382 millones
- **30 años:** $1,130 millones

¡Empezar 10 años antes puede significar TRIPLICAR tu resultado!

## La Regla del 72

Un truco rápido para saber en cuántos años se duplica tu dinero:

**72 ÷ tasa de interés = años para duplicar**

Ejemplos:
- Al 6% → 72 ÷ 6 = 12 años
- Al 10% → 72 ÷ 10 = 7.2 años
- Al 12% → 72 ÷ 12 = 6 años

## El enemigo silencioso: la inflación

El interés compuesto también trabaja EN TU CONTRA cuando hay inflación o cuando debes dinero con interés compuesto (como las tarjetas de crédito). Por eso es tan importante que tu dinero esté invertido y no debajo del colchón.""",
            "fun_fact": "Si Cristóbal Colón hubiera invertido $1 dólar en 1492 al 5% anual compuesto, hoy ese dólar valdría más de $40 mil millones de dólares. ¡El tiempo es el ingrediente secreto!",
            "difficulty": 2,
            "xp_reward": 80,
            "order": 1,
            "quiz": [
                {
                    "question": "¿Cuál es la diferencia clave entre interés simple y compuesto?",
                    "option_a": "El compuesto tiene tasas más altas",
                    "option_b": "En el compuesto ganas intereses sobre los intereses acumulados",
                    "option_c": "El simple es solo para bancos",
                    "correct_option": "b",
                    "explanation": "En el interés compuesto ganas rendimientos sobre tu capital inicial Y sobre los intereses ya ganados. Eso crea un efecto exponencial.",
                    "order": 1,
                },
                {
                    "question": "Según la Regla del 72, ¿en cuántos años se duplica tu dinero al 8% anual?",
                    "option_a": "6 años",
                    "option_b": "8 años",
                    "option_c": "9 años",
                    "option_d": "12 años",
                    "correct_option": "c",
                    "explanation": "72 ÷ 8 = 9 años. La Regla del 72 es un atajo rápido para estimar el tiempo de duplicación de una inversión.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es el mejor aliado del interés compuesto?",
                    "option_a": "Una tasa de interés altísima",
                    "option_b": "El tiempo",
                    "option_c": "Invertir grandes cantidades",
                    "correct_option": "b",
                    "explanation": "El tiempo es el mejor aliado del interés compuesto. Empezar antes, aunque sea con poco, genera resultados exponencialmente mayores a largo plazo.",
                    "order": 3,
                },
            ],
        },
    ],

    # ─── MÓDULO 5: Inversión Básica ────────────────────────────────────────
    "inversion-basica": [
        {
            "slug": "que-es-invertir",
            "title": "¿Qué es invertir y por qué deberías hacerlo?",
            "summary": "Invertir no es solo para ricos. Entiende los conceptos básicos y por qué dejar tu plata quieta te cuesta dinero.",
            "content": """# ¿Qué es invertir y por qué deberías hacerlo?

Invertir es poner tu dinero a trabajar para que **genere más dinero**. Es como plantar una semilla: con tiempo y las condiciones correctas, crece.

## ¿Por qué NO invertir te cuesta dinero?

Imagina que tienes $10,000,000 guardados. Si la inflación es del 8% anual, después de un año tu dinero tiene el poder de compra de $9,200,000. En 5 años, vale como $6,800,000.

**Guardar tu dinero sin invertir es perder dinero lentamente.**

## Conceptos clave que necesitas saber

### Rentabilidad 📊
Es cuánto gana tu inversión. Se expresa en porcentaje.
- CDT: ~10-12% anual (bajo riesgo)
- Fondos: ~12-18% anual (riesgo medio)
- Acciones: muy variable (alto riesgo)

### Riesgo ⚠️
La posibilidad de perder dinero. Regla fundamental: **mayor rentabilidad = mayor riesgo**.

### Diversificación 🎯
No pongas todos los huevos en una canasta. Distribuye tu dinero en diferentes inversiones para reducir el riesgo.

### Liquidez 💧
Qué tan rápido puedes convertir tu inversión en efectivo.

## Tipos de inversión (de menor a mayor riesgo)

1. **CDTs** — Certificados de Depósito a Término. Prestas tu dinero al banco por un plazo fijo.
2. **Fondos de inversión** — Un grupo de personas pone dinero en un fondo que un experto administra.
3. **ETFs** — Fondos que replican un índice (como el S&P 500). Diversificación instantánea.
4. **Acciones** — Compras una parte de una empresa. Si la empresa crece, tu inversión crece.
5. **Criptomonedas** — Activos digitales. Muy volátiles. Solo dinero que estés dispuesto a perder.

## ¿Cuándo empezar?

**Ahora.** No importa si es poco. El tiempo es tu mayor ventaja (recuerda el interés compuesto). Es mejor invertir $100,000 mensuales durante 20 años que $500,000 mensuales durante 5 años.

## Errores comunes del principiante

1. Esperar a "tener suficiente" para empezar
2. Invertir sin entender en qué
3. Entrar en pánico cuando el mercado baja
4. Poner todo el dinero en una sola inversión
5. Seguir "tips calientes" de redes sociales""",
            "fun_fact": "El índice S&P 500 ha tenido un rendimiento promedio del ~10% anual durante los últimos 90 años. Si hubieras invertido $1 millón en 1990, hoy tendrías más de $20 millones.",
            "difficulty": 2,
            "xp_reward": 80,
            "order": 1,
            "quiz": [
                {
                    "question": "¿Por qué guardar dinero sin invertir es malo?",
                    "option_a": "Porque los bancos te cobran comisiones",
                    "option_b": "Porque la inflación hace que tu dinero pierda poder de compra",
                    "option_c": "Porque es ilegal guardar mucho efectivo",
                    "correct_option": "b",
                    "explanation": "La inflación reduce el poder de compra de tu dinero con el tiempo. Si no inviertes, tu dinero vale menos cada año.",
                    "order": 1,
                },
                {
                    "question": "¿Qué significa 'diversificar' tus inversiones?",
                    "option_a": "Invertir solo en el activo más rentable",
                    "option_b": "Distribuir tu dinero en diferentes tipos de inversiones",
                    "option_c": "Cambiar de inversión cada mes",
                    "correct_option": "b",
                    "explanation": "Diversificar es distribuir tu dinero en diferentes inversiones para reducir el riesgo. Si una va mal, las otras pueden compensar.",
                    "order": 2,
                },
                {
                    "question": "¿Cuál es el orden correcto de menor a mayor riesgo?",
                    "option_a": "Acciones → CDTs → Fondos",
                    "option_b": "CDTs → Fondos/ETFs → Acciones",
                    "option_c": "ETFs → Criptomonedas → CDTs",
                    "correct_option": "b",
                    "explanation": "El orden de menor a mayor riesgo es: CDTs (bajo riesgo), Fondos/ETFs (riesgo medio), Acciones (alto riesgo), y Criptomonedas (muy alto riesgo).",
                    "order": 3,
                },
            ],
        },
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
#  LOGROS (ACHIEVEMENTS)
# ═══════════════════════════════════════════════════════════════════════════════

ACHIEVEMENTS = [
    {
        "slug": "primera-leccion",
        "title": "¡Primer Paso!",
        "description": "Completaste tu primera lección. El viaje de mil millas empieza con un paso.",
        "icon": "🎯",
        "xp_bonus": 50,
        "condition_type": "lessons_completed",
        "condition_value": 1,
    },
    {
        "slug": "estudiante-dedicado",
        "title": "Estudiante Dedicado",
        "description": "Completaste 5 lecciones. ¡Ya sabes más de finanzas que la mayoría!",
        "icon": "📚",
        "xp_bonus": 150,
        "condition_type": "lessons_completed",
        "condition_value": 5,
    },
    {
        "slug": "quiz-perfecto",
        "title": "Mente Brillante",
        "description": "Sacaste 100% en un quiz. ¡Perfección financiera!",
        "icon": "🧠",
        "xp_bonus": 100,
        "condition_type": "perfect_quiz",
        "condition_value": 1,
    },
    {
        "slug": "primer-modulo",
        "title": "Módulo Completado",
        "description": "Terminaste todas las lecciones de un módulo. ¡Nivel desbloqueado!",
        "icon": "🏆",
        "xp_bonus": 200,
        "condition_type": "module_completed",
        "condition_value": 1,
    },
    {
        "slug": "financiero-nivel-5",
        "title": "Gurú Financiero",
        "description": "Completaste 10 lecciones. Oficialmente sabes más que el 90% de las personas.",
        "icon": "👑",
        "xp_bonus": 300,
        "condition_type": "lessons_completed",
        "condition_value": 10,
    },
    {
        "slug": "racha-3-dias",
        "title": "En Racha",
        "description": "3 días seguidos aprendiendo. ¡La constancia es clave!",
        "icon": "🔥",
        "xp_bonus": 75,
        "condition_type": "streak",
        "condition_value": 3,
    },
    {
        "slug": "racha-7-dias",
        "title": "Imparable",
        "description": "7 días seguidos de aprendizaje. ¡Nada te detiene!",
        "icon": "⚡",
        "xp_bonus": 200,
        "condition_type": "streak",
        "condition_value": 7,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNCIÓN SEED
# ═══════════════════════════════════════════════════════════════════════════════

def seed_education_data(db: Session):
    """
    Puebla la base de datos con módulos, lecciones, quizzes y logros.
    Es idempotente: no duplica datos si ya existen.
    """
    # Seed Modules
    for mod_data in MODULES:
        existing = db.query(EducationModule).filter_by(slug=mod_data["slug"]).first()
        if not existing:
            module = EducationModule(**mod_data)
            db.add(module)
            db.flush()  # para obtener el ID
            print(f"  ✅ Módulo creado: {mod_data['title']}")

            # Seed Lessons for this module
            lessons_data = LESSONS.get(mod_data["slug"], [])
            for lesson_data in lessons_data:
                quiz_data = lesson_data.pop("quiz", [])
                lesson = Lesson(module_id=module.id, **lesson_data)
                db.add(lesson)
                db.flush()
                print(f"    📖 Lección creada: {lesson_data['title']}")

                # Seed Quiz Questions
                for q_data in quiz_data:
                    question = QuizQuestion(lesson_id=lesson.id, **q_data)
                    db.add(question)
                print(f"      ❓ {len(quiz_data)} preguntas de quiz creadas")
        else:
            print(f"  ⏭️  Módulo ya existe: {mod_data['title']}")

    # Seed Achievements
    for ach_data in ACHIEVEMENTS:
        existing = db.query(Achievement).filter_by(slug=ach_data["slug"]).first()
        if not existing:
            achievement = Achievement(**ach_data)
            db.add(achievement)
            print(f"  🏅 Logro creado: {ach_data['title']}")
        else:
            print(f"  ⏭️  Logro ya existe: {ach_data['title']}")

    db.commit()
    print("\n🎉 Seed de educación financiera completado!")

    
