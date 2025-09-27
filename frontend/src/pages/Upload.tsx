import { useNavigate } from "react-router-dom";
import { useState } from "react";
import FileDropzone from "../components/FileDropzone";
import { uploadFile } from "../lib/api";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const nav = useNavigate();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please choose a file");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await uploadFile(file);
      nav(`/jobs/${res.job_id}`);
    } catch (e: any) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Upload CV</h1>
      <p className="muted">PDF, JPG, or PNG. Single file per job.</p>
      <form className="mt-3" onSubmit={onSubmit}>
        <FileDropzone onFileSelected={setFile} selectedFile={file} />
        {error && <div className="error mt-2">{error}</div>}
        <div className="mt-3">
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Uploading…" : "Start Processing"}
          </button>
        </div>
      </form>
    </div>
  );
}

