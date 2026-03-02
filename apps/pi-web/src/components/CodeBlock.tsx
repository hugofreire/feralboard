import React from "react";
import { Highlight, themes } from "prism-react-renderer";

// Map common file extensions / markdown language tags to Prism language names
const LANG_MAP: Record<string, string> = {
  py: "python", python: "python",
  js: "javascript", javascript: "javascript",
  ts: "typescript", typescript: "typescript",
  tsx: "tsx", jsx: "jsx",
  json: "json",
  sh: "bash", bash: "bash", shell: "bash",
  css: "css", html: "markup", xml: "markup",
  yaml: "yaml", yml: "yaml",
  md: "markdown", markdown: "markdown",
  sql: "sql",
  c: "c", cpp: "cpp", "c++": "cpp",
  go: "go", rust: "rust", java: "java",
  env: "bash",
};

function detectLang(filename?: string, langHint?: string): string {
  if (langHint) {
    const mapped = LANG_MAP[langHint.toLowerCase()];
    if (mapped) return mapped;
  }
  if (filename) {
    const ext = filename.split(".").pop()?.toLowerCase() || "";
    const mapped = LANG_MAP[ext];
    if (mapped) return mapped;
  }
  return "python"; // sensible default for this project
}

interface CodeBlockProps {
  code: string;
  language?: string;
  filename?: string;
  showLineNumbers?: boolean;
  maxHeight?: string;
  className?: string;
}

export function CodeBlock({
  code,
  language,
  filename,
  showLineNumbers = true,
  maxHeight = "60vh",
  className = "",
}: CodeBlockProps) {
  const lang = detectLang(filename, language);

  return (
    <Highlight theme={themes.nightOwl} code={code.trimEnd()} language={lang}>
      {({ tokens, getLineProps, getTokenProps }) => (
        <pre
          className={`overflow-auto text-[0.78rem] leading-[1.6] ${className}`}
          style={{ maxHeight, margin: 0, background: "transparent" }}
        >
          <code>
            {tokens.map((line, i) => {
              const lineProps = getLineProps({ line, key: i });
              return (
                <div key={i} {...lineProps} style={{ ...lineProps.style, display: "flex" }}>
                  {showLineNumbers && (
                    <span
                      className="select-none text-right pr-4 shrink-0"
                      style={{
                        width: `${String(tokens.length).length * 0.7 + 1}em`,
                        color: "var(--color-muted-foreground)",
                        opacity: 0.35,
                      }}
                    >
                      {i + 1}
                    </span>
                  )}
                  <span className="flex-1">
                    {line.map((token, key) => (
                      <span key={key} {...getTokenProps({ token, key })} />
                    ))}
                  </span>
                </div>
              );
            })}
          </code>
        </pre>
      )}
    </Highlight>
  );
}

/**
 * Custom renderer for react-markdown code blocks.
 * Use with: <ReactMarkdown components={{ code: MarkdownCode }}>
 */
export function MarkdownCode({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLElement> & { children?: React.ReactNode }) {
  const match = /language-(\w+)/.exec(className || "");
  const isInline = !match && !String(children).includes("\n");

  if (isInline) {
    return <code className={className} {...props}>{children}</code>;
  }

  return (
    <CodeBlock
      code={String(children)}
      language={match?.[1]}
      showLineNumbers={true}
      maxHeight="50vh"
    />
  );
}
