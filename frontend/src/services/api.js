import axios from 'axios';
export const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
export const api=axios.create({baseURL:API});
export const wsUrl=()=>API.replace(/^http/,'ws')+'/ws';
