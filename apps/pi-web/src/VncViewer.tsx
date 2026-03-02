import React, { useRef, useEffect, useState, useCallback } from "react";
import RFB from "@novnc/novnc";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft, Maximize2, Minimize2, Monitor, Loader2, WifiOff,
} from "lucide-react";

// ── Reusable VNC panel (connection + canvas) ────────────────────

type VncStatus = "connecting" | "connected" | "disconnected";

export function VncPanel({ className }: { className?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rfbRef = useRef<any>(null);
  const [status, setStatus] = useState<VncStatus>("connecting");

  const connect = useCallback(() => {
    if (!containerRef.current) return;
    if (rfbRef.current) { rfbRef.current.disconnect(); rfbRef.current = null; }
    containerRef.current.innerHTML = "";
    setStatus("connecting");

    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${proto}//${window.location.host}/vnc-ws`;

    try {
      const rfb = new RFB(containerRef.current, wsUrl, { wsProtocols: ["binary"] });
      rfb.scaleViewport = true;
      rfb.resizeSession = false;
      rfb.showDotCursor = true;
      rfb.addEventListener("connect", () => setStatus("connected"));
      rfb.addEventListener("disconnect", () => { setStatus("disconnected"); rfbRef.current = null; });
      rfb.addEventListener("securityfailure", (e: any) => { console.error("[vnc] Security failure:", e.detail); setStatus("disconnected"); });
      rfbRef.current = rfb;
    } catch (err) {
      console.error("[vnc] Connection error:", err);
      setStatus("disconnected");
    }
  }, []);

  useEffect(() => {
    connect();
    return () => { if (rfbRef.current) { rfbRef.current.disconnect(); rfbRef.current = null; } };
  }, [connect]);

  return (
    <div className={`relative overflow-hidden bg-black ${className || ""}`}>
      <div ref={containerRef} className="w-full h-full" />

      {status === "connecting" && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80">
          <div className="text-center">
            <Loader2 className="size-6 text-primary animate-spin mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">Connecting...</p>
          </div>
        </div>
      )}

      {status === "disconnected" && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80">
          <div className="text-center">
            <WifiOff className="size-6 text-destructive/60 mx-auto mb-2" />
            <p className="text-xs text-muted-foreground mb-3">Disconnected</p>
            <Button variant="secondary" size="sm" onClick={connect}>Reconnect</Button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Full-page VNC viewer ────────────────────────────────────────

export default function VncViewer({ onBack }: { onBack: () => void }) {
  return (
    <div className="h-dvh flex flex-col bg-background text-foreground overflow-hidden">
      <header className="flex items-center gap-2 px-3 py-2 border-b border-sidebar-border shrink-0 bg-background/90 backdrop-blur-sm">
        <Button variant="ghost" size="icon" className="size-8" onClick={onBack}>
          <ArrowLeft className="size-4" />
        </Button>
        <Monitor className="size-4 text-primary" />
        <span className="text-sm font-semibold font-[var(--font-display)]">Device Screen</span>
        <span className="text-xs font-mono text-muted-foreground/60">VNC</span>
      </header>
      <VncPanel className="flex-1" />
    </div>
  );
}
