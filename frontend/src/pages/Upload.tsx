import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { AlertCircle } from "lucide-react";
import FileDropzone from "../components/FileDropzone";
import { useResumeUpload } from "../hooks/useResumeUpload";
import { PageWrapper, PageContainer } from "../components/styled";
import { APIError } from "../lib/api";

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
            maxWidth: "90%",
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
              }}>
                <div style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "var(--space-2)"
                }}>
                  <AlertCircle size={18} style={{ color: "var(--accent2-600)", flexShrink: 0, marginTop: "2px" }} />
                  <div>
                    <div style={{
                      color: "var(--accent2-700)",
                      fontSize: "var(--text-sm)",
                      fontWeight: 600,
                      marginBottom: "var(--space-1)"
                    }}>
                      {error.message || 'Upload failed'}
                    </div>
                    {error instanceof APIError && error.statusCode === 400 && (
                      <div style={{
                        color: "var(--neutral-600)",
                        fontSize: "var(--text-xs)",
                        lineHeight: 1.5
                      }}>
                        {error.message.includes("email") ? (
                          <>Make sure your resume contains a valid email address. The system uses email to identify and deduplicate resumes.</>
                        ) : error.message.includes("already exists") ? (
                          <>A resume with this email has already been uploaded. You can search for it or delete it first.</>
                        ) : (
                          <>Please check that your file is a valid resume document (PDF, DOCX, DOC, JPG, PNG).</>
                        )}
                      </div>
                    )}
                  </div>
                </div>
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
                    : "0 8px 24px rgba(var(--primary-700-rgb), 0.4)"
                }}
                onMouseEnter={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = "0 12px 32px rgba(var(--primary-700-rgb), 0.5)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isPending && file) {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(var(--primary-700-rgb), 0.4)";
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
