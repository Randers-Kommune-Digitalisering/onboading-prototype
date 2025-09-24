import axios from 'axios';

const API_URL = 'api';

export const deleteMail = (data) => {
  return axios.delete(`${API_URL}/mail/delete/${data.id}`);
};