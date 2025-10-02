import { useCallback, useState, useMemo } from "react";
import { useFileConfig } from "../hooks/useFileConfig";

type Props = {
  onFileSelected: (file: File) => void;
  selectedFile?: File | null;
};

export default function FileDropzone({ onFileSelected, selectedFile }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { data: fileConfig, isLoading } = useFileConfig();

  const { acceptedTypes, maxSizes, groupedBySize } = useMemo(() => {
    if (!fileConfig) {
      return { acceptedTypes: [], maxSizes: {}, groupedBySize: [] };
    }
    const types = Object.values(fileConfig).map(cfg => cfg.media_type);
    const sizes: Record<string, number> = {};
    Object.values(fileConfig).forEach(cfg => {
      sizes[cfg.media_type] = cfg.max_size_mb;
    });

    const sizeGroups: Record<number, string[]> = {};
    Object.entries(fileConfig).forEach(([ext, config]) => {
      const size = config.max_size_mb;
      if (!sizeGroups[size]) {
        sizeGroups[size] = [];
      }
      sizeGroups[size].push(ext.replace('.', '').toUpperCase());
    });

    const grouped = Object.entries(sizeGroups)
      .sort(([a], [b]) => Number(b) - Number(a))
      .map(([size, exts]) => ({
        size: Number(size),
        extensions: exts.sort()
      }));

    return { acceptedTypes: types, maxSizes: sizes, groupedBySize: grouped };
  }, [fileConfig]);

  const validate = (file: File) => {
    if (!fileConfig) {
      return "Configuration loading, please wait...";
    }
    if (!acceptedTypes.includes(file.type)) {
      const allExts = groupedBySize.flatMap(g => g.extensions).join(', ');
      return `Unsupported file type. Allowed: ${allExts}`;
    }
    const maxMb = maxSizes[file.type] ?? 10;
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
  }, [onFileSelected, validate]);

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const onPaste = (e: React.ClipboardEvent<HTMLDivElement>) => {
    e.preventDefault();
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.kind === 'file') {
        const file = item.getAsFile();
        if (file) {
          const err = validate(file);
          if (err) {
            setError(err);
            return;
          }
          setError(null);
          onFileSelected(file);
          return;
        }
      }
    }
  };

  return (
    <div>
      <div
        className={"dropzone" + (dragOver ? " drag" : "") + (selectedFile ? " has-file" : "")}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onPaste={onPaste}
        tabIndex={0}
      >
        <div className="dz-content">
          {selectedFile ? (
            <>
              <div className="dz-file-icon" style={{ fontSize: "48px", marginBottom: "var(--space-2)" }}>
                {selectedFile.type.startsWith("image/") ? "🖼️" : "📄"}
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
              <div className="dz-sub">
                {isLoading ? "Loading supported file types..." : "or click to choose a file of any supported type"}
              </div>
            </>
          )}
          <input
            type="file"
            accept={acceptedTypes.join(",")}
            className="file-input"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>
      {error && <div className="error mt-2">{error}</div>}
      {!isLoading && !selectedFile && fileConfig && groupedBySize.length > 0 && (
        <div style={{
          marginTop: "var(--space-1)",
          textAlign: "center",
          fontSize: "var(--text-xs)",
          color: "var(--neutral-600)",
          lineHeight: 1.6
        }}>
          {groupedBySize.map((group, idx) => (
            <span key={group.size}>
              <span style={{ fontWeight: 600, color: "var(--neutral-700)" }}>
                {group.extensions.join(', ')}
              </span>
              {' '}
              <span style={{ color: "var(--neutral-500)" }}>
                (max {group.size}MB)
              </span>
              {idx < groupedBySize.length - 1 && (
                <span style={{ margin: "0 var(--space-2)", color: "var(--neutral-400)" }}>•</span>
              )}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

