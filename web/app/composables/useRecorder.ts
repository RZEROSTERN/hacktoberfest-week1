const MAX_SECONDS = 60
const PREFERRED_TYPES = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus', 'audio/webm']

export type RecorderError = 'permission' | 'unsupported'

/** Records the microphone in memory with MediaRecorder; nothing is saved on the phone. */
export function useRecorder() {
  const recording = ref(false)
  const seconds = ref(0)
  let recorder: MediaRecorder | null = null
  let timer: ReturnType<typeof setInterval> | undefined
  let finish: ((blob: Blob) => void) | null = null

  function supported(): boolean {
    return typeof window !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined'
  }

  /** Starts recording; resolves with the audio when stop() is called or after 60 s. */
  async function start(): Promise<Blob> {
    if (!supported()) throw new Error('unsupported' satisfies RecorderError)
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    }
    catch {
      throw new Error('permission' satisfies RecorderError)
    }
    const mimeType = PREFERRED_TYPES.find(type => MediaRecorder.isTypeSupported(type))
    recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
    const chunks: Blob[] = []
    recorder.ondataavailable = event => chunks.push(event.data)

    const done = new Promise<Blob>((resolve) => {
      finish = resolve
    })
    recorder.onstop = () => {
      stream.getTracks().forEach(track => track.stop())
      clearInterval(timer)
      recording.value = false
      finish?.(new Blob(chunks, { type: recorder?.mimeType || 'audio/webm' }))
    }

    seconds.value = 0
    recording.value = true
    recorder.start()
    timer = setInterval(() => {
      seconds.value += 1
      if (seconds.value >= MAX_SECONDS) stop()
    }, 1000)
    return done
  }

  function stop() {
    if (recorder?.state === 'recording') recorder.stop()
  }

  onBeforeUnmount(stop)
  return { recording, seconds, start, stop, supported }
}
