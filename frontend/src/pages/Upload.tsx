import { useNavigate } from "react-router-dom";
import { useState } from "react";
import FileDropzone from "../components/FileDropzone";
import { useResumeUpload } from "../hooks/useResumeUpload";
import { Zap } from "lucide-react";
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
      <div className="decorative-blur decorative-blur-primary-top" />
      <div className="decorative-blur decorative-blur-primary-bottom" />

      <PageContainer>
        <div style={{
          textAlign: "center",
          marginBottom: "var(--space-10)"
        }}>
          <h1 style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(2.5rem, 6vw, 3.75rem)",
            fontWeight: 800,
            background: "linear-gradient(135deg, #0c0a09 0%, #292524 50%, #44403c 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            marginBottom: "var(--space-5)",
            lineHeight: 1.1,
            letterSpacing: "-0.02em"
          }}>
            Process Your Resume
          </h1>

          <p style={{
            fontSize: "var(--text-xl)",
            color: "var(--neutral-700)",
            lineHeight: 1.6,
            maxWidth: "620px",
            margin: "0 auto",
            fontWeight: 500
          }}>
            Upload your CV and extract structured data{" "}
            <span style={{
              background: "linear-gradient(120deg, #4338ca 0%, #6366f1 50%, #4338ca 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              fontWeight: 800,
              fontSize: "var(--text-2xl)",
              position: "relative",
              display: "inline-block",
              letterSpacing: "-0.01em"
            }}>
              instantly
            </span>
            {" "}with LLM-powered parsing
          </p>
        </div>

        <div className="glass-card" style={{
          padding: "var(--space-8)",
          boxShadow: "0 20px 60px rgba(67, 56, 202, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08)"
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
                  gap: "10px",
                  padding: "16px 40px",
                  fontSize: "var(--text-lg)",
                  fontWeight: 700,
                  fontFamily: "var(--font-body)",
                  color: "#ffffff",
                  background: isPending || !file
                    ? "#d4d4d8"
                    : "linear-gradient(135deg, #4338ca 0%, #6366f1 50%, #4338ca 100%)",
                  backgroundSize: isPending || !file ? "100% 100%" : "200% 100%",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  cursor: isPending || !file ? "not-allowed" : "pointer",
                  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                  boxShadow: isPending || !file
                    ? "none"
                    : "0 8px 24px rgba(67, 56, 202, 0.35), 0 2px 8px rgba(0, 0, 0, 0.1)",
                  position: "relative",
                  overflow: "hidden"
                }}
                onMouseEnter={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
                    e.currentTarget.style.boxShadow = "0 12px 32px rgba(67, 56, 202, 0.45), 0 4px 12px rgba(0, 0, 0, 0.15)";
                    e.currentTarget.style.backgroundPosition = "100% 0";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(0) scale(1)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(67, 56, 202, 0.35), 0 2px 8px rgba(0, 0, 0, 0.1)";
                    e.currentTarget.style.backgroundPosition = "0% 0";
                  }
                }}
              >
                <Zap size={20} strokeWidth={2.5} />
                {isPending ? "Processing…" : "Start Processing"}
              </button>
            </div>
          </form>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
