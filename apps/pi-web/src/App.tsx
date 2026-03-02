import React, { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { CodeBlock, MarkdownCode } from "@/components/CodeBlock";
import VncViewer, { VncPanel } from "./VncViewer";
import {
  ArrowUp, ArrowLeft, Check, X, Plus, Square, Loader2, Wrench,
  Monitor, RefreshCw, Camera, Trash2, Settings, Code, MessageSquare,
  FileText, Zap, ChevronRight, FolderOpen, File, ChevronDown,
  PanelRightOpen, PanelRightClose, GripVertical,
} from "lucide-react";

const mdComponents = { code: MarkdownCode };

// ── Types ───────────────────────────────────────────────────────

interface AppInfo {
  slug: string;
  name: string;
  description: string;
  type: "greeting" | "custom";
  greeting?: string;
  page?: string;
  hasEnv: boolean;
  hasPageFile: boolean;
  [key: string]: any;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: string[];
}

interface FileEntry {
  name: string;
  path: string;
  relativePath: string;
  size: number;
  isDir: boolean;
}

interface SessionInfo {
  id: string;
  timestamp: string;
  name: string;
  preview: string;
  messageCount: number;
  filePath: string;
  cwd: string;
  isCoding: boolean;
}

// ── Router ──────────────────────────────────────────────────────

type Route =
  | { page: "dashboard" }
  | { page: "vnc" }
  | { page: "agent"; slug: string }
  | { page: "config"; slug: string }
  | { page: "env"; slug: string }
  | { page: "create" };

function parseRoute(pathname: string): Route {
  if (pathname === "/vnc") return { page: "vnc" };
  if (pathname === "/apps/new") return { page: "create" };
  const agentMatch = pathname.match(/^\/apps\/([^/]+)\/agent$/);
  if (agentMatch) return { page: "agent", slug: agentMatch[1] };
  const configMatch = pathname.match(/^\/apps\/([^/]+)\/config$/);
  if (configMatch) return { page: "config", slug: configMatch[1] };
  const envMatch = pathname.match(/^\/apps\/([^/]+)\/env$/);
  if (envMatch) return { page: "env", slug: envMatch[1] };
  return { page: "dashboard" };
}

function routePath(route: Route): string {
  switch (route.page) {
    case "dashboard": return "/";
    case "vnc": return "/vnc";
    case "create": return "/apps/new";
    case "agent": return `/apps/${route.slug}/agent`;
    case "config": return `/apps/${route.slug}/config`;
    case "env": return `/apps/${route.slug}/env`;
  }
}

function useRouter() {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.pathname));

  useEffect(() => {
    const onPop = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = useCallback((r: Route) => {
    window.history.pushState(null, "", routePath(r));
    setRoute(r);
  }, []);

  return { route, navigate };
}

// ── App ─────────────────────────────────────────────────────────

export default function App() {
  const { route, navigate } = useRouter();
  const [apps, setApps] = useState<AppInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [screenshotKey, setScreenshotKey] = useState(0);

  useEffect(() => { fetchApps(); }, []);

  const fetchApps = async () => {
    try { setApps(await (await fetch("/api/apps")).json()); } catch {}
  };

  const restartGui = async () => {
    setLoading(true);
    try {
      await fetch("/api/system/restart-gui", { method: "POST" });
      setTimeout(async () => { await takeScreenshot(); setLoading(false); }, 3000);
    } catch { setLoading(false); }
  };

  const takeScreenshot = async () => {
    try {
      await fetch("/api/system/screenshot", { method: "POST" });
      setScreenshotKey((k) => k + 1);
      setScreenshotUrl(`/api/system/screenshot?t=${Date.now()}`);
    } catch {}
  };

  const deleteApp = async (slug: string) => {
    if (!confirm(`Delete app "${slug}"? This removes the app directory and page file.`)) return;
    try { await fetch(`/api/apps/${slug}`, { method: "DELETE" }); fetchApps(); } catch {}
  };

  // Resolve app name for agent view (need it from the apps list)
  const getAppName = (slug: string) => apps.find((a) => a.slug === slug)?.name || slug;

  return (
    <div className="h-dvh flex flex-col bg-background text-foreground overflow-hidden">
      {route.page === "dashboard" && (
        <Dashboard
          apps={apps} loading={loading}
          screenshotUrl={screenshotUrl} screenshotKey={screenshotKey}
          onRefresh={fetchApps} onRestartGui={restartGui} onScreenshot={takeScreenshot}
          onOpenAgent={(slug) => navigate({ page: "agent", slug })}
          onOpenConfig={(slug) => navigate({ page: "config", slug })}
          onOpenEnv={(slug) => navigate({ page: "env", slug })}
          onCreate={() => navigate({ page: "create" })}
          onDelete={deleteApp}
          onOpenVnc={() => navigate({ page: "vnc" })}
        />
      )}
      {route.page === "agent" && (
        <AgentView
          slug={route.slug}
          appName={getAppName(route.slug)}
          onBack={() => { navigate({ page: "dashboard" }); fetchApps(); }}
          onRestartGui={restartGui}
          onScreenshot={takeScreenshot}
          screenshotUrl={screenshotUrl}
          screenshotKey={screenshotKey}
        />
      )}
      {route.page === "config" && (
        <ConfigEditor slug={route.slug} onBack={() => { navigate({ page: "dashboard" }); fetchApps(); }} />
      )}
      {route.page === "env" && (
        <EnvEditor slug={route.slug} onBack={() => { navigate({ page: "dashboard" }); fetchApps(); }} />
      )}
      {route.page === "create" && (
        <CreateApp
          onBack={() => navigate({ page: "dashboard" })}
          onCreated={() => { fetchApps(); navigate({ page: "dashboard" }); }}
        />
      )}
      {route.page === "vnc" && (
        <VncViewer onBack={() => navigate({ page: "dashboard" })} />
      )}
    </div>
  );
}

// ── Dashboard ───────────────────────────────────────────────────

function Dashboard({
  apps, loading, screenshotUrl, screenshotKey,
  onRefresh, onRestartGui, onScreenshot,
  onOpenAgent, onOpenConfig, onOpenEnv, onCreate, onDelete, onOpenVnc,
}: {
  apps: AppInfo[];
  loading: boolean;
  screenshotUrl: string | null;
  screenshotKey: number;
  onRefresh: () => void;
  onRestartGui: () => void;
  onScreenshot: () => void;
  onOpenAgent: (slug: string) => void;
  onOpenConfig: (slug: string) => void;
  onOpenEnv: (slug: string) => void;
  onCreate: () => void;
  onDelete: (slug: string) => void;
  onOpenVnc: () => void;
}) {
  return (
    <>
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
        <span className="text-base font-semibold font-[var(--font-display)]">
          <span className="text-primary-light">Feral</span>Board Portal
        </span>
        <div className="flex-1" />
        <Button variant="ghost" size="sm" onClick={onOpenVnc} title="Live device screen (VNC)">
          <Monitor className="size-3.5" />
          <span className="ml-1">Screen</span>
        </Button>
        <Button variant="ghost" size="sm" onClick={onScreenshot} title="Take screenshot">
          <Camera className="size-3.5" />
        </Button>
        <Button
          variant="secondary" size="sm"
          onClick={onRestartGui}
          disabled={loading}
          title="Restart GUI + Screenshot"
        >
          {loading ? <Loader2 className="size-3.5 animate-spin" /> : <RefreshCw className="size-3.5" />}
          <span className="ml-1">Restart GUI</span>
        </Button>
      </header>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 max-md:px-3">
          {/* App grid */}
          <div className="flex items-center gap-4 mb-4">
            <h2 className="font-mono text-[10px] uppercase tracking-[3px] text-primary shrink-0">Kiosk Apps</h2>
            <div className="flex-1 h-px bg-rule" />
            <Button size="sm" onClick={onCreate}>
              <Plus className="size-3.5" /> New App
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
            {apps.map((app) => (
              <div
                key={app.slug}
                className={cn(
                  "border border-border rounded-lg bg-card p-4 flex flex-col gap-3 border-l-[3px]",
                  app.type === "custom" ? "border-l-primary" : "border-l-muted-foreground/30"
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0">
                    <div className="font-mono text-[11px] uppercase tracking-wider font-semibold truncate">{app.name}</div>
                    <div className="text-xs text-muted-foreground mt-0.5 truncate">{app.description}</div>
                  </div>
                  <Badge variant={app.type === "custom" ? "primary" : "default"} className="shrink-0 ml-2">
                    {app.type === "custom" ? "custom" : "greeting"}
                  </Badge>
                </div>

                <div className="flex items-center gap-1.5 text-xs text-muted-foreground/60 font-mono">
                  <span>kiosk_apps/{app.slug}/</span>
                  {app.type === "custom" && app.hasPageFile && (
                    <span className="text-primary/60">+ gui/pages/{app.page}.py</span>
                  )}
                </div>

                <div className="flex gap-2 mt-auto">
                  <Button variant="ghost" size="sm" onClick={() => onOpenConfig(app.slug)} title="Edit app.json">
                    <FileText className="size-3.5" /> Config
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onOpenEnv(app.slug)} title="Edit .env">
                    <Settings className="size-3.5" /> Env
                  </Button>
                  {app.type === "custom" && (
                    <Button size="sm" onClick={() => onOpenAgent(app.slug)} title="Open AI coding agent">
                      <Code className="size-3.5" /> Agent
                    </Button>
                  )}
                  <div className="flex-1" />
                  <Button variant="ghost" size="sm" className="text-destructive/60 hover:text-destructive" onClick={() => onDelete(app.slug)} title="Delete app">
                    <Trash2 className="size-3.5" />
                  </Button>
                </div>
              </div>
            ))}

            {apps.length === 0 && (
              <div className="col-span-2 text-center text-muted-foreground/40 py-12 text-sm">
                No kiosk apps found. Create your first one!
              </div>
            )}
          </div>

          {/* Screenshot preview */}
          {screenshotUrl && (
            <div className="mb-6">
              <div className="flex items-center gap-4 mb-3">
                <h2 className="font-mono text-[10px] uppercase tracking-[3px] text-primary shrink-0">Device Screen</h2>
                <div className="flex-1 h-px bg-rule" />
              </div>
              <div className="border border-border rounded-lg overflow-hidden bg-black inline-block">
                <img
                  key={screenshotKey}
                  src={screenshotUrl}
                  alt="Device screenshot"
                  className="max-h-[400px] w-auto"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// ── Resizable VNC Sidebar (drag handle) ─────────────────────────

function useResizablePanel(defaultWidth: number, minWidth: number, maxWidth: number) {
  const [width, setWidth] = useState(defaultWidth);
  const [isOpen, setIsOpen] = useState(false);
  const dragging = useRef(false);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;

    const onMouseMove = (ev: MouseEvent) => {
      if (!dragging.current) return;
      const newWidth = window.innerWidth - ev.clientX;
      setWidth(Math.max(minWidth, Math.min(maxWidth, newWidth)));
    };

    const onMouseUp = () => {
      dragging.current = false;
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  }, [minWidth, maxWidth]);

  return { width, isOpen, setIsOpen, onMouseDown };
}

// ── Agent Chat View ─────────────────────────────────────────────

function AgentView({
  slug, appName, onBack, onRestartGui, onScreenshot, screenshotUrl, screenshotKey,
}: {
  slug: string;
  appName: string;
  onBack: () => void;
  onRestartGui: () => void;
  onScreenshot: () => void;
  screenshotUrl: string | null;
  screenshotKey: number;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [previewFile, setPreviewFile] = useState<{ path: string; content: string; relativePath: string } | null>(null);
  const [scopeSent, setScopeSent] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const vnc = useResizablePanel(400, 200, 800);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  // Load files and sessions on mount
  useEffect(() => {
    fetchFiles();
    fetchSessions();
  }, [slug]);

  const fetchFiles = async () => {
    try { setFiles(await (await fetch(`/api/apps/${slug}/files`)).json()); } catch {}
  };

  const fetchSessions = async () => {
    try {
      const all: SessionInfo[] = await (await fetch("/api/sessions")).json();
      setSessions(all.filter((s) => s.isCoding));
    } catch {}
  };

  const openFile = async (filePath: string) => {
    try {
      const data = await (await fetch(`/api/files/read?path=${encodeURIComponent(filePath)}`)).json();
      setPreviewFile(data);
    } catch {}
  };

  const switchSession = async (s: SessionInfo) => {
    try {
      await fetch("/api/sessions/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionPath: s.filePath, cwd: s.cwd }),
      });
      const msgs = await (await fetch("/api/sessions/messages")).json();
      setMessages(msgs);
      setScopeSent(true);
    } catch {}
  };

  const newSession = async () => {
    try {
      await fetch("/api/new-session", { method: "POST" });
      setMessages([]);
      setScopeSent(false);
      fetchSessions();
    } catch {}
  };

  const buildScopePrefix = () => [
    `[Context: You are working on the kiosk app "${appName}" (slug: "${slug}").`,
    `Files in scope: kiosk_apps/${slug}/app.json, kiosk_apps/${slug}/.env, gui/pages/${slug}.py`,
    `Read kiosk_apps/CLAUDE.md for the full development guide. Read the app files before making changes.]`,
    ``,
  ].join("\n");

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    setStreamingText("");
    setActiveTools([]);

    let actualMessage = text;
    if (!scopeSent) {
      actualMessage = buildScopePrefix() + text;
      setScopeSent(true);
    }

    let accumulated = "";
    const tools: string[] = [];

    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: actualMessage }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "delta") { accumulated += event.text; setStreamingText(accumulated); }
            else if (event.type === "tool_start") {
              const label = `${event.tool}${event.args?.command ? `: ${event.args.command.slice(0, 60)}` : ""}`;
              tools.push(label); setActiveTools([...tools]);
            }
            else if (event.type === "tool_end") setActiveTools([]);
            else if (event.type === "error") { accumulated += `\n\n> Error: ${event.error}`; setStreamingText(accumulated); }
          } catch {}
        }
      }

      setMessages((prev) => [...prev, {
        role: "assistant", content: accumulated || "No response",
        toolCalls: tools.length ? tools : undefined,
      }]);
      setStreamingText("");
      fetchSessions();
    } catch (err: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${err.message}` }]);
      setStreamingText("");
    } finally { setSending(false); setActiveTools([]); }
  }, [sending, scopeSent, slug, appName]);

  const abort = async () => { try { await fetch("/api/abort", { method: "POST" }); } catch {} };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  // Group files by directory
  const dirs = new Map<string, FileEntry[]>();
  for (const f of files) {
    if (f.isDir) continue;
    const dir = f.relativePath.includes("/") ? f.relativePath.slice(0, f.relativePath.lastIndexOf("/")) : ".";
    if (!dirs.has(dir)) dirs.set(dir, []);
    dirs.get(dir)!.push(f);
  }

  const formatDate = (ts: string) => {
    const d = new Date(ts);
    const diff = Date.now() - d.getTime();
    if (diff < 86400000) return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    if (diff < 604800000) return d.toLocaleDateString([], { weekday: "short" });
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  };

  return (
    <div className="flex h-full">
      {/* ── Left Sidebar ── */}
      <aside className="w-60 min-w-60 bg-sidebar-background border-r border-sidebar-border flex flex-col max-md:hidden">
        {/* File explorer (top) */}
        <div className="border-b border-sidebar-border">
          <div className="flex items-center justify-between px-3 py-2">
            <span className="font-mono text-[10px] uppercase tracking-[3px] text-primary">Files</span>
          </div>
          <div className="overflow-y-auto max-h-[40vh] px-1 pb-2">
            {[...dirs.entries()].map(([dir, dirFiles]) => (
              <div key={dir}>
                <div className="flex items-center gap-1.5 px-2 py-1 text-[0.65rem] text-muted-foreground/60 font-mono">
                  <FolderOpen className="size-3 shrink-0" />
                  <span className="truncate">{dir}/</span>
                </div>
                {dirFiles.map((f) => (
                  <button
                    key={f.path}
                    className={cn(
                      "flex items-center gap-1.5 w-full text-left bg-transparent border-0 px-2 py-1 pl-5 rounded cursor-pointer text-[0.7rem] font-mono truncate",
                      previewFile?.path === f.path
                        ? "bg-accent text-foreground"
                        : "text-muted-foreground hover:bg-card/60 hover:text-foreground"
                    )}
                    onClick={() => openFile(f.path)}
                    title={f.relativePath}
                  >
                    <File className="size-3 shrink-0" />
                    <span className="truncate">{f.name}</span>
                    <span className="ml-auto text-muted-foreground/30 shrink-0">
                      {f.size < 1024 ? `${f.size}B` : `${(f.size / 1024).toFixed(1)}K`}
                    </span>
                  </button>
                ))}
              </div>
            ))}
            {files.length === 0 && (
              <div className="text-center text-muted-foreground/30 py-4 text-[0.65rem]">No files</div>
            )}
          </div>
        </div>

        {/* Sessions (bottom) */}
        <div className="flex items-center justify-between px-3 py-2">
          <span className="font-mono text-[10px] uppercase tracking-[3px] text-primary">Sessions</span>
          <Button variant="ghost" size="icon" className="size-6" onClick={newSession} title="New session">
            <Plus className="size-3" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto px-1 pb-2">
          {sessions.map((s) => (
            <button
              key={s.id}
              className="block w-full text-left bg-transparent border border-transparent text-foreground px-2 py-1.5 rounded cursor-pointer mb-px hover:bg-card/60"
              onClick={() => switchSession(s)}
            >
              <div className="text-[0.7rem] truncate text-muted-foreground">{s.preview || s.name}</div>
              <div className="flex justify-between text-[0.6rem] text-muted-foreground/40 mt-0.5">
                <span>{formatDate(s.timestamp)}</span>
                <span>{s.messageCount} msgs</span>
              </div>
            </button>
          ))}
          {sessions.length === 0 && (
            <div className="text-center text-muted-foreground/30 py-4 text-[0.65rem]">No sessions yet</div>
          )}
        </div>
      </aside>

      {/* ── Main area ── */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="flex items-center gap-2 px-3 py-2 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
          <Button variant="ghost" size="icon" className="size-8" onClick={onBack}>
            <ArrowLeft className="size-4" />
          </Button>
          <Code className="size-4 text-primary" />
          <span className="text-sm font-semibold font-[var(--font-display)] truncate">{appName}</span>
          <span className="text-xs font-mono text-muted-foreground/60 truncate max-md:hidden">kiosk_apps/{slug}/</span>
          <div className="flex-1" />
          <Button variant="ghost" size="sm" onClick={onScreenshot} title="Screenshot">
            <Camera className="size-3.5" />
          </Button>
          <Button variant="secondary" size="sm" onClick={onRestartGui} title="Restart GUI">
            <RefreshCw className="size-3.5" /> <span className="max-md:hidden">Restart</span>
          </Button>
          <Button
            variant={vnc.isOpen ? "default" : "ghost"}
            size="sm"
            onClick={() => vnc.setIsOpen(!vnc.isOpen)}
            title={vnc.isOpen ? "Hide device screen" : "Show device screen"}
            className="max-md:hidden"
          >
            {vnc.isOpen ? <PanelRightClose className="size-3.5" /> : <PanelRightOpen className="size-3.5" />}
            <span className="ml-1">Screen</span>
          </Button>
        </header>

        {/* File preview banner */}
        {previewFile && (
          <div className="border-b border-sidebar-border shrink-0">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-surface">
              <File className="size-3 text-muted-foreground" />
              <span className="text-xs font-mono text-muted-foreground truncate">{previewFile.relativePath}</span>
              <div className="flex-1" />
              <Button variant="ghost" size="icon" className="size-6" onClick={() => setPreviewFile(null)}>
                <X className="size-3" />
              </Button>
            </div>
            <div className="bg-[#011627] rounded-b">
              <CodeBlock
                code={previewFile.content}
                filename={previewFile.relativePath}
                showLineNumbers={true}
                maxHeight="30vh"
                className="px-3 py-2"
              />
            </div>
          </div>
        )}

        <div className="flex flex-1 min-h-0">
          {/* ── Chat column ── */}
          <div className="flex flex-col flex-1 min-w-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-3 max-md:px-3 flex flex-col gap-3">
              {messages.length === 0 && !streamingText && !sending && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <Code className="size-8 text-muted-foreground/20 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground/40 mb-1">Ready to code</p>
                    <p className="text-xs text-muted-foreground/30">Describe what you want the agent to do with {appName}</p>
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <div key={i} className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
                  <div
                    className={cn(
                      "max-w-[80%] max-md:max-w-[90%] text-sm leading-relaxed",
                      msg.role === "user"
                        ? "bg-primary/15 text-foreground px-3.5 py-2 rounded-2xl rounded-br-sm"
                        : "px-1"
                    )}
                  >
                    {msg.toolCalls && (
                      <div className="flex flex-wrap gap-1 mb-1.5">
                        {msg.toolCalls.map((t, j) => (
                          <span key={j} className="inline-flex items-center gap-1 text-[0.65rem] text-muted-foreground/50 font-mono">
                            <Wrench className="size-2.5" />{t}
                          </span>
                        ))}
                      </div>
                    )}
                    {msg.role === "assistant" ? (
                      <div className="prose prose-sm prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>{msg.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <pre className="whitespace-pre-wrap break-words font-mono text-[0.84rem]">{msg.content}</pre>
                    )}
                  </div>
                </div>
              ))}

              {streamingText && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] max-md:max-w-[90%] text-sm leading-relaxed px-1">
                    {activeTools.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-1.5">
                        {activeTools.map((t, j) => (
                          <span key={j} className="inline-flex items-center gap-1 text-[0.65rem] text-primary-light/80 font-mono">
                            <Loader2 className="size-2.5 animate-spin" />{t}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="prose prose-sm prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>{streamingText}</ReactMarkdown>
                      <span className="cursor-blink text-muted-foreground/40">|</span>
                    </div>
                  </div>
                </div>
              )}

              {sending && !streamingText && (
                <div className="flex justify-start px-1">
                  <div className="flex items-center gap-1.5">
                    <span className="loading-dot text-sm text-muted-foreground">*</span>
                    <span className="loading-dot text-sm text-muted-foreground">*</span>
                    <span className="loading-dot text-sm text-muted-foreground">*</span>
                  </div>
                </div>
              )}

              {sending && (
                <div className="flex justify-center">
                  <button
                    className="text-xs text-muted-foreground/50 hover:text-destructive cursor-pointer bg-transparent border-0 flex items-center gap-1 transition-colors"
                    onClick={abort}
                  >
                    <Square className="size-3" /> Stop
                  </button>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Screenshot thumbnail */}
            {screenshotUrl && !vnc.isOpen && (
              <div className="px-4 py-2 border-t border-sidebar-border shrink-0 flex items-center gap-3">
                <img
                  key={screenshotKey}
                  src={screenshotUrl}
                  alt="Screen"
                  className="h-16 w-auto rounded border border-border"
                />
                <span className="text-xs text-muted-foreground/40">Latest screenshot</span>
              </div>
            )}

            {/* Input */}
            <div className="flex items-end gap-2 px-4 py-2.5 max-md:px-3 max-md:py-2 border-t border-sidebar-border shrink-0 pb-safe">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you want the agent to do..."
                rows={1}
                disabled={sending}
                className="flex-1 min-w-0 min-h-[38px] max-h-[120px] rounded-xl text-sm py-2.5 px-3"
              />
              <Button
                onClick={() => sendMessage(input)}
                disabled={sending || !input.trim()}
                size="icon"
                className="size-[38px] rounded-xl shrink-0"
              >
                <ArrowUp className="size-4" />
              </Button>
            </div>
          </div>

          {/* ── VNC Sidebar ── */}
          {vnc.isOpen && (
            <>
              {/* Drag handle */}
              <div
                className="w-1.5 shrink-0 cursor-col-resize bg-sidebar-border hover:bg-primary/40 active:bg-primary/60 transition-colors flex items-center justify-center group"
                onMouseDown={vnc.onMouseDown}
              >
                <GripVertical className="size-3 text-muted-foreground/30 group-hover:text-muted-foreground/60" />
              </div>

              {/* VNC panel */}
              <div className="shrink-0 flex flex-col border-l border-sidebar-border" style={{ width: vnc.width }}>
                <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-sidebar-border bg-sidebar-background/90 backdrop-blur-sm shrink-0">
                  <Monitor className="size-3 text-primary" />
                  <span className="font-mono text-[10px] uppercase tracking-[3px] text-primary">Device Screen</span>
                  <div className="flex-1" />
                  <Button variant="ghost" size="icon" className="size-5" onClick={() => vnc.setIsOpen(false)} title="Close">
                    <X className="size-3" />
                  </Button>
                </div>
                <VncPanel className="flex-1" />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Config Editor (app.json) ────────────────────────────────────

function ConfigEditor({ slug, onBack }: { slug: string; onBack: () => void }) {
  const [config, setConfig] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/api/apps/${slug}`);
        const data = await res.json();
        const { slug: _, type, hasEnv, hasPageFile, manifestPath, ...manifest } = data;
        setConfig(JSON.stringify(manifest, null, 4));
      } catch {}
    };
    load();
  }, [slug]);

  const save = async () => {
    setError("");
    try {
      const parsed = JSON.parse(config);
      setSaving(true);
      const res = await fetch(`/api/apps/${slug}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      if (!res.ok) throw new Error("Save failed");
      onBack();
    } catch (err: any) {
      setError(err.message || "Invalid JSON");
    } finally { setSaving(false); }
  };

  return (
    <>
      <header className="flex items-center gap-2 px-3 py-2 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
        <Button variant="ghost" size="icon" className="size-8" onClick={onBack}>
          <ArrowLeft className="size-4" />
        </Button>
        <FileText className="size-4 text-muted-foreground" />
        <span className="text-sm font-semibold font-[var(--font-display)]">app.json</span>
        <span className="text-xs font-mono text-muted-foreground/60">kiosk_apps/{slug}/</span>
        <div className="flex-1" />
        <Button size="sm" onClick={save} disabled={saving}>
          {saving ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />}
          Save
        </Button>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto">
          {error && (
            <div className="text-sm text-destructive mb-3 p-3 rounded bg-tint-accent border-l-[3px] border-destructive">
              {error}
            </div>
          )}
          <textarea
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            className="w-full h-[60vh] bg-surface border border-border rounded-lg p-4 font-mono text-sm text-foreground resize-none focus:outline-none focus:border-primary"
            spellCheck={false}
          />
        </div>
      </div>
    </>
  );
}

// ── Env Editor (.env key-value) ─────────────────────────────────

function EnvEditor({ slug, onBack }: { slug: string; onBack: () => void }) {
  const [vars, setVars] = useState<[string, string][]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await (await fetch(`/api/apps/${slug}/env`)).json();
        setVars(Object.entries(data));
      } catch {}
    };
    load();
  }, [slug]);

  const save = async () => {
    setSaving(true);
    try {
      const obj: Record<string, string> = {};
      for (const [k, v] of vars) {
        if (k.trim()) obj[k.trim()] = v;
      }
      await fetch(`/api/apps/${slug}/env`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj),
      });
      onBack();
    } catch {} finally { setSaving(false); }
  };

  const addRow = () => setVars([...vars, ["", ""]]);
  const removeRow = (i: number) => setVars(vars.filter((_, j) => j !== i));
  const updateKey = (i: number, key: string) => {
    const next = [...vars]; next[i] = [key, next[i][1]]; setVars(next);
  };
  const updateValue = (i: number, value: string) => {
    const next = [...vars]; next[i] = [next[i][0], value]; setVars(next);
  };

  return (
    <>
      <header className="flex items-center gap-2 px-3 py-2 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
        <Button variant="ghost" size="icon" className="size-8" onClick={onBack}>
          <ArrowLeft className="size-4" />
        </Button>
        <Settings className="size-4 text-muted-foreground" />
        <span className="text-sm font-semibold font-[var(--font-display)]">.env</span>
        <span className="text-xs font-mono text-muted-foreground/60">kiosk_apps/{slug}/</span>
        <div className="flex-1" />
        <Button size="sm" onClick={save} disabled={saving}>
          {saving ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />}
          Save
        </Button>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto flex flex-col gap-2">
          {vars.map(([k, v], i) => (
            <div key={i} className="flex gap-2 items-center">
              <Input
                value={k}
                onChange={(e) => updateKey(i, e.target.value)}
                placeholder="KEY"
                className="w-48 font-mono text-xs"
              />
              <span className="text-muted-foreground">=</span>
              <Input
                value={v}
                onChange={(e) => updateValue(i, e.target.value)}
                placeholder="value"
                className="flex-1 font-mono text-xs"
              />
              <Button variant="ghost" size="icon" className="size-8" onClick={() => removeRow(i)}>
                <X className="size-3.5 text-destructive/60" />
              </Button>
            </div>
          ))}

          <Button variant="ghost" size="sm" className="self-start mt-2" onClick={addRow}>
            <Plus className="size-3.5" /> Add Variable
          </Button>

          {vars.length === 0 && (
            <div className="text-center text-muted-foreground/40 py-12 text-sm">
              No environment variables. Click "Add Variable" to create one.
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// ── Create App ──────────────────────────────────────────────────

function CreateApp({ onBack, onCreated }: { onBack: () => void; onCreated: (slug: string) => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState<"greeting" | "custom">("custom");
  const [greeting, setGreeting] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  const create = async () => {
    if (!name.trim()) return;
    setCreating(true);
    setError("");
    try {
      const res = await fetch("/api/apps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, type, greeting }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed");
      onCreated(data.slug);
    } catch (err: any) {
      setError(err.message);
    } finally { setCreating(false); }
  };

  return (
    <>
      <header className="flex items-center gap-2 px-3 py-2 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
        <Button variant="ghost" size="icon" className="size-8" onClick={onBack}>
          <ArrowLeft className="size-4" />
        </Button>
        <Plus className="size-4 text-muted-foreground" />
        <span className="text-sm font-semibold font-[var(--font-display)]">New App</span>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-md mx-auto flex flex-col gap-4">
          {error && (
            <div className="text-sm text-destructive p-3 rounded bg-tint-accent border-l-[3px] border-destructive">
              {error}
            </div>
          )}

          <div>
            <label className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My App"
              autoFocus
            />
            {slug && (
              <div className="text-xs text-muted-foreground/50 mt-1 font-mono">
                slug: {slug}
              </div>
            )}
          </div>

          <div>
            <label className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Description</label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What this app does..."
            />
          </div>

          <div>
            <label className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-2 block">Type</label>
            <div className="flex gap-2">
              <button
                className={cn(
                  "flex-1 p-3 rounded-lg border text-left transition-colors cursor-pointer border-l-[3px]",
                  type === "custom"
                    ? "border-l-primary border-primary/40 bg-primary/10"
                    : "border-l-transparent border-border bg-card hover:bg-accent"
                )}
                onClick={() => setType("custom")}
              >
                <div className="text-sm font-medium flex items-center gap-2">
                  <Code className="size-4" /> Custom Page
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  GTK page with full control. Agent can edit the code.
                </div>
              </button>
              <button
                className={cn(
                  "flex-1 p-3 rounded-lg border text-left transition-colors cursor-pointer border-l-[3px]",
                  type === "greeting"
                    ? "border-l-primary border-primary/40 bg-primary/10"
                    : "border-l-transparent border-border bg-card hover:bg-accent"
                )}
                onClick={() => setType("greeting")}
              >
                <div className="text-sm font-medium flex items-center gap-2">
                  <MessageSquare className="size-4" /> Greeting
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Simple text shown on lock screen. No code needed.
                </div>
              </button>
            </div>
          </div>

          {type === "greeting" && (
            <div>
              <label className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-1 block">Greeting Text</label>
              <Input
                value={greeting}
                onChange={(e) => setGreeting(e.target.value)}
                placeholder="Hello World!"
              />
            </div>
          )}

          {type === "custom" && slug && (
            <div className="text-xs text-muted-foreground/60 p-3 rounded bg-tint-accent border-l-[3px] border-primary/40 font-mono">
              <div>Will create:</div>
              <div className="mt-1">kiosk_apps/{slug}/app.json</div>
              <div>kiosk_apps/{slug}/.env</div>
              <div>gui/pages/{slug}.py</div>
            </div>
          )}

          <Button
            onClick={create}
            disabled={creating || !name.trim()}
            className="mt-2"
          >
            {creating ? <Loader2 className="size-4 animate-spin" /> : <Zap className="size-4" />}
            Create App
          </Button>
        </div>
      </div>
    </>
  );
}
