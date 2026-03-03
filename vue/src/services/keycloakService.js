import axios from 'axios';

let CACHED_USER_INFO = null;
let IN_FLIGHT_USER_INFO_PROMISE = null;

const ROLE_ADMIN = 'Admin';
const ROLE_ANSVARLIG = 'Ansvarlig';
const ROLE_NY_MEDARBEJDER = 'Ny medarbejder';

function toArray(value) {
    return Array.isArray(value) ? value : [];
}

function defaultPublicUserInfo() {
    return {
        roles: ['Public'],
        isAdmin: false,
        isAnsvarlig: false,
        isMedarbejder: false,
    };
}

function normalizeUserInfo(rawUserInfo) {
    const roles = toArray(rawUserInfo?.roles);
    const isAdmin = roles.includes(ROLE_ADMIN);
    const isAnsvarlig = roles.includes(ROLE_ANSVARLIG);
    const isMedarbejder = roles.includes(ROLE_NY_MEDARBEJDER) || (!isAdmin && !isAnsvarlig);

    return {
        ...(rawUserInfo ?? {}),
        roles,
        isAdmin,
        isAnsvarlig,
        isMedarbejder,
    };
}

export const getUserInfoFromBackend = () => {
    // Leading slash avoids route-relative requests like /forloeb-overview/api/userinfo
    return axios.get('/api/userinfo');
};

export async function getUserInfo() {
    if (CACHED_USER_INFO) {
        return CACHED_USER_INFO;
    }

    if (IN_FLIGHT_USER_INFO_PROMISE) {
        return IN_FLIGHT_USER_INFO_PROMISE;
    }

    IN_FLIGHT_USER_INFO_PROMISE = (async () => {
        console.log('Fetching user info from backend...');
        try {
            const response = await getUserInfoFromBackend();
            const normalized = normalizeUserInfo(response?.data);
            CACHED_USER_INFO = normalized;
            return normalized;
        } catch (error) {
            console.warn('No user info:', error);
            const fallback = defaultPublicUserInfo();
            CACHED_USER_INFO = fallback;
            return fallback;
        } finally {
            IN_FLIGHT_USER_INFO_PROMISE = null;
        }
    })();

    return IN_FLIGHT_USER_INFO_PROMISE;
}