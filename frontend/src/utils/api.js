// Centralized API calls to Django backend

const API_BASE_URL = 'http://https://smartpdf-bge7.onrender.com/api';

// Helper function for API calls
async function apiCall(endpoint, method, body, isFile = false) {
  const options = {
    method: method,
    headers: isFile ? {} : { 'Content-Type': 'application/json' },
  };
  
  if (body) {
    options.body = isFile ? body : JSON.stringify(body);
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'API call failed');
  }
  
  return response;
}

// PDF Operations
export const uploadPDF = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiCall('/upload/', 'POST', formData, true);
};

export const replaceText = (file, textElements) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('text_elements', JSON.stringify(textElements));
  return apiCall('/replace-text/', 'POST', formData, true);
};

export const deletePages = (file, pages) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('pages', pages);
  return apiCall('/delete-pages/', 'POST', formData, true);
};

export const insertImage = (file, imageFile, pageNumber, x, y) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image', imageFile);
  formData.append('page', pageNumber);
  formData.append('x', x);
  formData.append('y', y);
  return apiCall('/insert-image/', 'POST', formData, true);
};

export const mergePDFs = (files) => {
  const formData = new FormData();
  files.forEach((file, index) => {
    formData.append(`file_${index}`, file);
  });
  return apiCall('/merge-pdf/', 'POST', formData, true);
};

export const splitPDF = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiCall('/split/', 'POST', formData, true);
};

export const extractPages = (file, pages) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('pages', pages);
  return apiCall('/extract-pages/', 'POST', formData, true);
};

export const getPDFPreview = (pageNum) => {
  return apiCall(`/preview/${pageNum}/`, 'GET');
};