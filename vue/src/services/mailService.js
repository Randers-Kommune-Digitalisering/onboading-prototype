import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const NEW_TASK_ANSVARLIG = 'NEW_TASK_ANSVARLIG';
export const NEW_TASK_USER = 'NEW_TASK_USER';

export const deleteMail = (data) => {
  return apiRequest({ method: 'delete', url: `${API_URL}/mail/delete/${data.id}` });
};

export const sendWelcomeMail = (forloebId, content) => {
  return apiRequest({ method: 'post', url: `${API_URL}/forloeb/${forloebId}/send-welcome`, data: content });
};