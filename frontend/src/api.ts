import axios from 'axios';

const API_BASE = 'http://backend:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'X-API-KEY': localStorage.getItem("apiKey") || "",
  }
});
