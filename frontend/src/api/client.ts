import { API_URL } from './config';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${path.startsWith('/') ? path : `/${path}`}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options?.headers || {}),
  };

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    let responseData: any = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      responseData = await response.json();
    } else {
      responseData = await response.text();
    }

    if (!response.ok) {
      const errorMsg = (responseData && typeof responseData === 'object' && responseData.detail)
        ? responseData.detail 
        : `Erro na requisição (Status ${response.status})`;
      throw new ApiError(errorMsg, response.status, responseData);
    }

    return responseData as T;
  } catch (error) {
    console.error(`[API Client Error] Fetching ${url} failed:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Não foi possível conectar ao servidor. Verifique se o backend do DaTabela está ativo.');
  }
}

export const client = {
  get: <T>(path: string, options?: RequestInit) => request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body: any, options?: RequestInit) => request<T>(path, { 
    ...options, 
    method: 'POST', 
    body: JSON.stringify(body) 
  }),
};
