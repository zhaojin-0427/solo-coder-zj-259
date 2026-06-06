import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error('API Error:', err)
    return Promise.reject(err)
  }
)

export type ListResp<T> = { results: T[]; count: number; next: string | null; previous: string | null }

export const cellarPoolApi = {
  list: () => api.get<any, ListResp<any>>('/cellar-pools/?page_size=100'),
  create: (data: any) => api.post('/cellar-pools/', data),
  update: (id: number, data: any) => api.put(`/cellar-pools/${id}/`, data),
  delete: (id: number) => api.delete(`/cellar-pools/${id}/`),
}

export const batchApi = {
  list: (params?: any) => api.get<any, ListResp<any>>('/batches/', { params: { page_size: 100, ...params } }),
  create: (data: any) => api.post('/batches/', data),
  update: (id: number, data: any) => api.put(`/batches/${id}/`, data),
  delete: (id: number) => api.delete(`/batches/${id}/`),
  complete: (id: number) => api.post(`/batches/${id}/complete/`),
  curve: (id: number) => api.get(`/batches/${id}/curve/`),
  updateRisk: (id: number, data: any) => api.post(`/batches/${id}/update_risk/`, data),
}

export const recordApi = {
  list: (params?: any) => api.get<any, ListResp<any>>('/fermentation-records/', { params: { page_size: 200, ...params } }),
  create: (data: any) => api.post('/fermentation-records/', data),
  update: (id: number, data: any) => api.put(`/fermentation-records/${id}/`, data),
  delete: (id: number) => api.delete(`/fermentation-records/${id}/`),
}

export const qualityApi = {
  list: () => api.get<any, ListResp<any>>('/wine-qualities/?page_size=100'),
  create: (data: any) => api.post('/wine-qualities/', data),
  update: (id: number, data: any) => api.put(`/wine-qualities/${id}/`, data),
  delete: (id: number) => api.delete(`/wine-qualities/${id}/`),
}

export const storageApi = {
  list: () => api.get<any, ListResp<any>>('/aging-storages/?page_size=100'),
  create: (data: any) => api.post('/aging-storages/', data),
  update: (id: number, data: any) => api.put(`/aging-storages/${id}/`, data),
  delete: (id: number) => api.delete(`/aging-storages/${id}/`),
}

export const agingRecordApi = {
  list: (params?: any) => api.get<any, ListResp<any>>('/aging-records/', { params: { page_size: 100, ...params } }),
  create: (data: any) => api.post('/aging-records/', data),
  update: (id: number, data: any) => api.put(`/aging-records/${id}/`, data),
  delete: (id: number) => api.delete(`/aging-records/${id}/`),
  finish: (id: number) => api.post(`/aging-records/${id}/finish/`),
}

export const envRecordApi = {
  list: (params?: any) => api.get<any, ListResp<any>>('/aging-env-records/', { params: { page_size: 200, ...params } }),
  create: (data: any) => api.post('/aging-env-records/', data),
}

export const statsApi = {
  overview: () => api.get('/stats/overview/'),
  yieldRate: () => api.get('/stats/yield_rate/'),
  gradeDistribution: () => api.get('/stats/grade_distribution/'),
  fermentationCycle: () => api.get('/stats/fermentation_cycle/'),
  agingLoss: () => api.get('/stats/aging_loss/'),
  monthlyOutput: () => api.get('/stats/monthly_output/'),
  disposalStats: () => api.get('/stats/disposal_stats/'),
}

export const disposalTaskApi = {
  list: (params?: any) => api.get<any, ListResp<any>>('/disposal-tasks/', { params: { page_size: 200, ...params } }),
  create: (data: any) => api.post('/disposal-tasks/', data),
  update: (id: number, data: any) => api.put(`/disposal-tasks/${id}/`, data),
  delete: (id: number) => api.delete(`/disposal-tasks/${id}/`),
  startProcess: (id: number, data?: any) => api.post(`/disposal-tasks/${id}/start_process/`, data || {}),
  submitDisposal: (id: number, data: any) => api.post(`/disposal-tasks/${id}/submit_disposal/`, data),
  review: (id: number, data: any) => api.post(`/disposal-tasks/${id}/review/`, data),
}

export default api
