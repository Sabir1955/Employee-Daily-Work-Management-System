import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
})

export const getErrorMessage = (error) =>
  error?.response?.data?.error || error?.message || 'Something went wrong. Please try again.'

export default api
