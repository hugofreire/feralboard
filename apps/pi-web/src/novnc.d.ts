declare module "@novnc/novnc" {
  export default class RFB {
    constructor(target: HTMLElement, url: string, options?: Record<string, any>);
    scaleViewport: boolean;
    resizeSession: boolean;
    showDotCursor: boolean;
    disconnect(): void;
    addEventListener(type: string, listener: (e: any) => void): void;
    removeEventListener(type: string, listener: (e: any) => void): void;
  }
}
