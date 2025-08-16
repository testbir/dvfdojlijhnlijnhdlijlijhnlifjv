// src/api/coursesApi.ts



import api from './axiosInstance';


export const getCourses = async () => {
  const response = await api.get('/admin/courses/');
  return response.data;
};

export const createCourse = async (data: any) => {
  const response = await api.post('/admin/courses', data);
  return response.data;
};
