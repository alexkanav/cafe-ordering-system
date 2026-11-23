import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { config } from '../../config';


export default function ImageUploader({ setNewImage }) {
  const [image, setImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    setImage(e.target.files[0]);
  };

  const uploadImage = async (e) => {
    e.preventDefault();
    if (!image) return;

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('image', image);

      const response = await fetch(`${config.API_URL}/api/admin/images`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const message = errorData?.detail || response.statusText || "Upload failed";
        throw new Error(message);
      }

      const result = await response.json();
      setNewImage(result.filename);
    } catch (error) {
      toast.error(`Помилка завантаження: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={uploadImage}>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button type="submit" disabled={!image || isUploading}>
        {isUploading ? 'Завантажую...' : 'Завантажити'}
      </button>
    </form>
  );
}