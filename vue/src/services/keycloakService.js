import axios from 'axios';

var USER_INFO = null;
const adminString = 'Admin';
const ansvarligString = 'Ansvarlig';
const medarbejderString = 'Medarbejder';

export const getUserInfoFromBackend = () => {
    return axios.get(`api/userinfo`);
};

export async function getUserInfo() {
    if (!USER_INFO) {
      console.log('Fetching user info from backend...');
      const res = await getUserInfoFromBackend();
      USER_INFO = res.data;
      USER_INFO.isAdmin = USER_INFO.roles.includes(adminString);
      USER_INFO.isAnsvarlig = USER_INFO.roles.includes(ansvarligString);
      USER_INFO.isMedarbejder = USER_INFO.roles.includes(medarbejderString);
    }
    return USER_INFO;
}