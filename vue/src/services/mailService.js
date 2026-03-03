import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const deleteMail = (data) => {
  return apiRequest({ method: 'delete', url: `${API_URL}/mail/delete/${data.id}` });
};