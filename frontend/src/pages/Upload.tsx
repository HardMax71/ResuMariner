import { useNavigate } from "react-router-dom";
import { useState } from "react";
import FileDropzone from "../components/FileDropzone";
import { useResumeUpload } from "../hooks/useResumeUpload";
import { PageWrapper, PageContainer } from "../components/styled";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const { mutate: uploadResume, isPending, error } = useResumeUpload();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    uploadResume(file, {
      onSuccess: (data) => {
        navigate(`/resumes/${data.uid}`);
      },
    });
  };

  return (
    <PageWrapper>
      <PageContainer>
        <div style={{
          textAlign: "center",
          marginBottom: "var(--space-10)"
        }}>
          <h1 style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(2.5rem, 6vw, 3.5rem)",
            fontWeight: 800,
            color: "var(--neutral-900)",
            marginBottom: "var(--space-4)",
            lineHeight: 1.1,
            letterSpacing: "-0.03em"
          }}>
            Process Your Resume
          </h1>

          <p style={{
            fontSize: "var(--text-xl)",
            color: "var(--neutral-600)",
            lineHeight: 1.6,
            maxWidth: "620px",
            margin: "0 auto"
          }}>
            Upload your CV and extract structured data instantly with LLM-powered parsing
          </p>
        </div>

        <div className="glass-card" style={{
          padding: "var(--space-8)"
        }}>
          <form onSubmit={onSubmit}>
            <FileDropzone onFileSelected={setFile} selectedFile={file} />

            {error && (
              <div style={{
                marginTop: "var(--space-3)",
                padding: "var(--space-3)",
                background: "var(--accent2-50)",
                border: "1px solid var(--accent2-200)",
                borderRadius: "var(--radius-sm)",
                color: "var(--accent2-700)",
                fontSize: "var(--text-sm)",
                fontWeight: 600
              }}>
                {error.message || 'Upload failed'}
              </div>
            )}

            <div style={{
              marginTop: "var(--space-6)",
              display: "flex",
              justifyContent: "center"
            }}>
              <button
                type="submit"
                disabled={isPending || !file}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "16px 32px",
                  fontSize: "var(--text-base)",
                  fontWeight: 700,
                  fontFamily: "var(--font-body)",
                  color: "white",
                  background: isPending || !file
                    ? "var(--neutral-300)"
                    : "linear-gradient(135deg, var(--primary-700) 0%, var(--primary-600) 100%)",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  cursor: isPending || !file ? "not-allowed" : "pointer",
                  transition: "all 0.3s",
                  boxShadow: isPending || !file
                    ? "none"
                    : "0 8px 24px rgba(67, 56, 202, 0.4)"
                }}
                onMouseEnter={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = "0 12px 32px rgba(67, 56, 202, 0.5)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(67, 56, 202, 0.4)";
                  }
                }}
              >
                {isPending ? "Processing…" : "Start Processing"}
              </button>
            </div>
          </form>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
