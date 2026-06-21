import { client } from './client';
import { AskResponse } from '../types/ask';

export const askQuestion = (question: string): Promise<AskResponse> => {
  return client.post<AskResponse>('/ask', { question });
};

export const getAskExamples = (): Promise<{ examples: string[] }> => {
  return client.get<{ examples: string[] }>('/ask/examples');
};

export const getAskIntents = (): Promise<any> => {
  return client.get<any>('/ask/intents');
};
