import { useEffect, useState } from "react";
import plantumlEncoder from "plantuml-encoder";

interface PlantUMLDiagramProps {
  src: string;
  alt?: string;
  caption?: string;
}

export default function PlantUMLDiagram({ src, alt = "PlantUML Diagram", caption }: PlantUMLDiagramProps) {
  const [imageUrl, setImageUrl] = useState<string>("");

  useEffect(() => {
    const fetchAndEncode = async () => {
      try {
        const response = await fetch(src);
        const pumlContent = await response.text();
        const encoded = plantumlEncoder.encode(pumlContent);
        setImageUrl(`https://www.plantuml.com/plantuml/png/${encoded}`);
      } catch (error) {
        console.error("Error loading PlantUML diagram:", error);
      }
    };

    fetchAndEncode();
  }, [src]);

  if (!imageUrl) {
    return (
      <div style={{
        border: "1px solid rgba(129, 140, 248, 0.2)",
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
        border: "1px solid rgba(129, 140, 248, 0.2)",
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
