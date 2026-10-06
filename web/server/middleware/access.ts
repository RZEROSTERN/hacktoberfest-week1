// Every page and API call needs the family access cookie, except the login itself
// and the static files the browser needs to show the login page (see isPublicPath).
export default defineEventHandler((event) => {
  const path = getRequestURL(event).pathname
  if (isPublicPath(path)) return

  const { accessCode } = useRuntimeConfig(event)
  if (isValidCode(getCookie(event, ACCESS_COOKIE), accessCode)) return

  if (path.startsWith('/api/')) {
    throw createError({ statusCode: 401, statusMessage: 'Unauthorized' })
  }
  return sendRedirect(event, '/acceso', 302)
})
