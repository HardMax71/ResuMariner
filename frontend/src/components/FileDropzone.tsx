import { useCallback, useState } from "react";

type Props = {
  onFileSelected: (file: File) => void;
  selectedFile?: File | null;
};

const ACCEPTED = [
  "application/pdf",
  "image/jpeg",
  "image/png"
];

const MAX_MB: Record<string, number> = {
  "application/pdf": 10,
  "image/jpeg": 5,
  "image/png": 5
};

export default function FileDropzone({ onFileSelected, selectedFile }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (file: File) => {
    if (!ACCEPTED.includes(file.type)) {
      return "Unsupported file type. PDF, JPG, or PNG only.";
    }
    const maxMb = MAX_MB[file.type] ?? 10;
    if (file.size > maxMb * 1024 * 1024) {
      return `File too large. Max ${maxMb}MB for this type.`;
    }
    return null;
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const err = validate(file);
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    onFileSelected(file);
  }, [onFileSelected]);

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <div
        className={"dropzone" + (dragOver ? " drag" : "") + (selectedFile ? " has-file" : "")}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <div className="dz-content">
          {selectedFile ? (
            <>
              <div className="dz-file-icon" style={{ fontSize: "48px", marginBottom: "var(--space-2)" }}>
                {selectedFile.type === "application/pdf" ? "📄" : "🖼️"}
              </div>
              <div className="dz-title">{selectedFile.name}</div>
              <div className="dz-sub">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                <span style={{ margin: "0 var(--space-2)" }}>•</span>
                Click to change
              </div>
            </>
          ) : (
            <>
              <div className="dz-title">Drop your CV here</div>
              <div className="dz-sub">or click to choose a file (PDF, JPG, PNG)</div>
            </>
          )}
          <input
            type="file"
            accept={ACCEPTED.join(",")}
            className="file-input"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>
      {error && <div className="error mt-2">{error}</div>}
    </div>
  );
}

