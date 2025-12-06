import { useMutation } from '@tanstack/react-query';
import { uploadResume } from '../services/resumeService';

export function useResumeUpload() {
  return useMutation({
    mutationFn: (file: File) => uploadResume(file),
  });
}
