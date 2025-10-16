import { useMutation } from '@tanstack/react-query';
import { uploadResume, type UploadResult } from '../services/resumeService';

export function useResumeUpload() {
  return useMutation({
    mutationFn: (file: File) => uploadResume(file),
    onSuccess: (data) => {
      console.log('Upload successful:', data.uid);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });
}
