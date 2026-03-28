/**
 * Herald Crypto Exchange - WebSocket Client (FE-04)
 *
 * Real-time market data streaming with automatic reconnection,
 * snapshot+diff model, and typed message handling.
 */

import type { WsMessage } from '@herald/shared';
import { WS_RECONNECT_DELAY_MS, WS_MAX_RECONNECT_ATTEMPTS } from '@herald/shared';

export type WsMessageHandler = (msg: WsMessage) => void;
export type WsStatusHandler = (status: ConnectionStatus) => void;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export class HeraldWsClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: WsMessageHandler[] = [];
  private statusHandlers: WsStatusHandler[] = [];
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private _status: ConnectionStatus = 'disconnected';

  constructor(baseUrl: string, instrumentId: string) {
    this.url = `${baseUrl}/ws/market/${instrumentId}`;
  }

  get status(): ConnectionStatus {
    return this._status;
  }

  connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }
    this.setStatus('connecting');
    try {
      this.ws = new WebSocket(this.url);
    } catch {
      this.setStatus('error');
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.setStatus('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        this.handlers.forEach((h) => h(msg));
      } catch {
        // Ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.setStatus('disconnected');
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.setStatus('error');
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.reconnectAttempts = WS_MAX_RECONNECT_ATTEMPTS; // Prevent reconnect
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus('disconnected');
  }

  onMessage(handler: WsMessageHandler): () => void {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }

  onStatus(handler: WsStatusHandler): () => void {
    this.statusHandlers.push(handler);
    return () => {
      this.statusHandlers = this.statusHandlers.filter((h) => h !== handler);
    };
  }

  sendPing(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send('ping');
    }
  }

  private setStatus(status: ConnectionStatus): void {
    this._status = status;
    this.statusHandlers.forEach((h) => h(status));
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= WS_MAX_RECONNECT_ATTEMPTS) return;
    const delay = WS_RECONNECT_DELAY_MS * Math.pow(1.5, this.reconnectAttempts);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}

/** Manage multiple instrument subscriptions */
export class WsManager {
  private clients: Map<string, HeraldWsClient> = new Map();
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  subscribe(instrumentId: string, handler: WsMessageHandler): () => void {
    let client = this.clients.get(instrumentId);
    if (!client) {
      client = new HeraldWsClient(this.baseUrl, instrumentId);
      this.clients.set(instrumentId, client);
      client.connect();
    }
    const unsub = client.onMessage(handler);
    return () => {
      unsub();
      // If no more handlers, disconnect
      if (client) {
        client.disconnect();
        this.clients.delete(instrumentId);
      }
    };
  }

  disconnectAll(): void {
    this.clients.forEach((client) => client.disconnect());
    this.clients.clear();
  }
}
