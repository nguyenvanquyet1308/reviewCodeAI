import axios from 'axios';

// When running locally, Vite proxies or communicates directly with port 8000.
// In docker/prod, Nginx proxies requests to the backend container under the same host.
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default client;
