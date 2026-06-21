export const getErrorMessage = (error: unknown): string => {
  if (!error) return 'Erro desconhecido';
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'object' && 'message' in error) {
    return String((error as any).message);
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return JSON.stringify(error);
};
