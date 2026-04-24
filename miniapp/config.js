window.APP_CONFIG = {
  BACKEND_BASE_URL: window.location.hostname.includes('localhost')
    ? 'http://localhost:8000'
    : 'https://your-render-api.onrender.com',
  TOURNAMENT_SLUG: 'world-cup-2026-demo'
};
