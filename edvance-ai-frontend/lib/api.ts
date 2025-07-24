// API utility for authenticated requests
function getFullUrl(url: string) {
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  const base = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!base) throw new Error('NEXT_PUBLIC_BACKEND_URL is not set');
  return base.replace(/\/$/, '') + (url.startsWith('/') ? url : '/' + url);
}

export async function apiFetch(url: string, options: RequestInit = {}) {
  const idToken = typeof window !== 'undefined' ? localStorage.getItem('idToken') : null;
  const headers = new Headers(options.headers || {});
  if (idToken) {
    headers.set('Authorization', `Bearer ${idToken}`);
  }
  return fetch(getFullUrl(url), { ...options, headers });
} 