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

  voice: {
    comingSoon: 'Muy pronto podrá preguntarme con su voz.'
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
