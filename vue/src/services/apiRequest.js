import axios from 'axios';

function normalizeMethod(method) {
  return (method || 'get').toString().toLowerCase();
}

/**
 * Generic Axios wrapper.
 *
 * - Always performs the Axios request inside try/catch.
 * - Any error is re-thrown.
 */
export async function apiRequest({ method = 'get', url, data, config } = {}) {
  const normalizedMethod = normalizeMethod(method);

  try {
    const requestConfig = {
      method: normalizedMethod,
      url,
      ...(config || {}),
    };

    if (data !== undefined) {
      requestConfig.data = data;
    }

    return await axios.request(requestConfig);
  } catch (error) {
    throw error;
  }
}
