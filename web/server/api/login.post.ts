export default defineEventHandler(async (event) => {
  const { accessCode } = useRuntimeConfig(event)
  const body = await readBody<{ code?: string }>(event)
  const code = body?.code?.trim()

  if (!isValidCode(code, accessCode)) {
    throw createError({ statusCode: 401, statusMessage: 'Unauthorized' })
  }

  setCookie(event, ACCESS_COOKIE, code!, {
    httpOnly: true,
    sameSite: 'lax',
    secure: !import.meta.dev,
    path: '/',
    maxAge: 60 * 60 * 24 * 365
  })
  return { ok: true }
})
