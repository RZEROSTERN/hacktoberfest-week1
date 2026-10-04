// Every user-facing string lives here, in warm, simple Mexican Spanish.
export const t = {
  appName: 'Traductor de Papeles',
  tagline: 'Le explico sus papeles en palabras sencillas.',

  home: {
    takePhoto: 'Tomar foto',
    askVoice: 'Preguntar con voz',
    history: 'Mis papeles',
    hint: 'Tome una foto de su recibo, carta o aviso, y yo le digo qué es y qué hacer.'
  },

  access: {
    title: 'Bienvenida',
    label: 'Escriba el código familiar',
    submit: 'Entrar',
    wrong: 'Ese código no es correcto. Pídaselo a su hijo.',
    error: 'No pude revisar el código. Intente de nuevo en un momento.'
  },

  photo: {
    reading: 'Estoy leyendo su papel…',
    readingHint: 'Esto puede tardar hasta un minuto. No cierre la pantalla.',
    preparing: 'Preparando la foto…',
    tryAgain: 'Tomar otra foto',
    errorTitle: 'Algo salió mal',
    errorNetwork: 'No me pude conectar. Revise su internet e intente de nuevo.',
    errorTooBig: 'La foto es muy pesada. Intente tomarla de nuevo.',
    errorType: 'Ese archivo no es una foto. Use el botón "Tomar foto".',
    errorGeneric: 'No pude leer la foto en este momento. Intente de nuevo en un rato.'
  },

  result: {
    fraudTitle: '¡Cuidado! Esto podría ser un fraude',
    fraudNever: 'Nunca dé contraseñas, NIP, números de tarjeta ni datos personales.',
    lowConfidenceTitle: 'No pude leer bien su papel',
    whatIs: '¿Qué es?',
    from: 'Lo envía',
    whenAndHowMuch: '¿Cuándo y cuánto?',
    deadline: 'Fecha límite',
    amount: 'Cantidad a pagar',
    noDeadline: 'No encontré una fecha límite.',
    noAmount: 'No encontré una cantidad a pagar.',
    whatToDo: '¿Qué tengo que hacer?',
    nothingToDo: 'Por ahora no tiene que hacer nada.',
    addToCalendar: 'Agregar a mi calendario',
    disclaimer: 'Solo le explico el papel; no es asesoría legal ni financiera. Si es algo serio, platíquelo con su hijo o con un profesional.',
    home: 'Volver al inicio',
    notFound: 'No encontré ese papel.'
  },

  history: {
    title: 'Mis papeles',
    upcoming: 'Próximas fechas',
    all: 'Todos mis papeles',
    empty: 'Todavía no hay papeles. Tome una foto para empezar.',
    noUpcoming: 'No tiene fechas límite próximas.',
    due: 'Vence',
    today: 'Hoy',
    tomorrow: 'Mañana',
    inDays: (days: number) => `En ${days} días`,
    suspicious: 'Posible fraude',
    scanned: 'Lo revisamos el'
  },

  voice: {
    title: 'Pregúnteme con su voz',
    aboutDocument: 'Su pregunta es sobre este papel:',
    hint: 'Toque el botón, haga su pregunta y luego toque "Ya terminé".',
    start: 'Empezar a hablar',
    stop: 'Ya terminé',
    recording: 'Le estoy escuchando…',
    listening: 'Estoy pensando su respuesta…',
    listeningHint: 'Esto puede tardar hasta un minuto.',
    youAsked: 'Usted preguntó',
    answer: 'Mi respuesta',
    askAgain: 'Hacer otra pregunta',
    askAboutThis: 'Preguntar sobre este papel',
    errorTitle: 'No pude escucharle',
    errorPermission: 'Necesito permiso para usar el micrófono. Toque "Permitir" cuando el teléfono le pregunte.',
    errorUnsupported: 'Este teléfono no me deja grabar. Pídale ayuda a su hijo.',
    errorAudio: 'No pude oír la grabación. Intente de nuevo.',
    seconds: (s: number) => `${s} s`
  },

  common: {
    loading: 'Cargando…',
    back: 'Volver'
  }
} as const

export function formatMoney(amount: number): string {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(amount)
}

export function formatDate(isoDate: string): string {
  // Dates are calendar days (YYYY-MM-DD); parse as local noon to avoid timezone shifts.
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'full' }).format(new Date(`${isoDate}T12:00:00`))
}

/** Whole days from today (local) until an ISO calendar date. */
export function daysUntil(isoDate: string, today: Date = new Date()): number {
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const [y, m, d] = isoDate.split('-').map(Number) as [number, number, number]
  return Math.round((new Date(y, m - 1, d).getTime() - start.getTime()) / 86_400_000)
}

export function formatShortDate(isoDate: string): string {
  return new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(isoDate.length === 10 ? `${isoDate}T12:00:00` : isoDate))
}
