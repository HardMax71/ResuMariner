import { useEffect, useState } from "react";
import pako from "pako";

interface PlantUMLDiagramProps {
  src: string;
  alt?: string;
  caption?: string;
  format?: "svg" | "png";
}

function encodeForKroki(source: string): string {
  const data = new TextEncoder().encode(source);
  const compressed = pako.deflate(data, { level: 9 });
  const base64 = btoa(String.fromCharCode(...compressed));
  return base64.replace(/\+/g, "-").replace(/\//g, "_");
}

export default function PlantUMLDiagram({ src, alt = "PlantUML Diagram", caption, format = "svg" }: PlantUMLDiagramProps) {
  const [imageUrl, setImageUrl] = useState<string>("");

  useEffect(() => {
    const fetchAndEncode = async () => {
      try {
        const response = await fetch(src);
        const pumlContent = await response.text();
        const encoded = encodeForKroki(pumlContent);
        setImageUrl(`https://kroki.io/plantuml/${format}/${encoded}`);
      } catch (error) {
        console.error("Error loading PlantUML diagram:", error);
      }
    };

    fetchAndEncode();
  }, [src, format]);

  if (!imageUrl) {
    return (
      <div style={{
        border: "1px solid rgba(var(--primary-400-rgb), 0.2)",
        borderRadius: "var(--radius-sm)",
        padding: "var(--space-4)",
        textAlign: "center",
        color: "var(--neutral-500)"
      }}>
        Loading diagram...
      </div>
    );
  }

  return (
    <div>
      <div style={{
        border: "1px solid rgba(var(--primary-400-rgb), 0.2)",
        borderRadius: "var(--radius-sm)",
        overflow: "hidden",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}>
        <img
          src={imageUrl}
          alt={alt}
          style={{
            maxWidth: "100%",
            height: "auto",
            display: "block"
          }}
        />
      </div>
      {caption && (
        <p style={{
          color: "var(--neutral-600)",
          fontSize: "var(--text-sm)",
          marginTop: "var(--space-3)",
          fontStyle: "italic",
          textAlign: "center"
        }}>
          {caption}
        </p>
      )}
    </div>
  );
}
