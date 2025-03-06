import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createOpgave = (data) => {
  return axios.post(`${API_URL}/opgave`, data);
};

export const getOpgaverByForloebIDAdmin = (forloebID) => {
  return axios.get(`${API_URL}/opgave/forloeb/admin/${forloebID}`);
};

export const getOpgaverByForloebID = async (forloebID, config) => {
  try {
    const response = await axios.get(`${API_URL}/opgave/forloeb/${forloebID}`, config);
    return response;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return { data: [] }; // Return an empty array or any other custom response
    }
    throw error; // Re-throw the error if it's not a 404
  }
}

export const getOpgaverByForloebsskabelonID = (forloebsskabelonID, config) => {
  return axios.get(`${API_URL}/opgave/forloebsskabelon/${forloebsskabelonID}`, config);
};
  
  export const deleteOpgave = (opgaveID) => {
    return axios.delete(`${API_URL}/opgave/${opgaveID}`);
};
  
  export const updateOpgave = (opgaveID, data) => {
    return axios.put(`${API_URL}/opgave/${opgaveID}`, data);
};

  export const getOpgaver = () => {
    return axios.get(`${API_URL}/opgave`);
};

export const createOpgaveWithOpgaveskabelon = (data) => {
  return axios.post(`${API_URL}/opgave/opgaveskabelon`, data);
};