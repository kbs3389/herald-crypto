/**
 * Herald Crypto Exchange - Trade Page (FE-08)
 * Main trading interface with orderbook, trades, and order entry.
 */
import React, { useCallback } from 'react';
import type { PlaceOrderRequest, Instrument, OrderResponse } from '@herald/shared';
import { OrderBookView } from '../components/market/OrderBookView';
import { RecentTrades } from '../components/market/RecentTrades';
import { TickerBar } from '../components/market/TickerBar';
import { CandlestickChart } from '../components/market/CandlestickChart';
import { OrderEntry } from '../components/order/OrderEntry';
import { useOrderBook, useRecentTrades, useTicker, useApiClient } from '../hooks/useApi';

interface Props {
  instruments: Instrument[];
  selectedInstrument: string;
  token: string | null;
  onSelectInstrument: (id: string) => void;
  onOrderPlaced?: (order: OrderResponse) => void;
}

export const TradePage: React.FC<Props> = ({
  instruments, selectedInstrument, token, onSelectInstrument, onOrderPlaced,
}) => {
  const orderBook = useOrderBook(selectedInstrument);
  const trades = useRecentTrades(selectedInstrument);
  const ticker = useTicker(selectedInstrument);
  const client = useApiClient();

  const handleOrder = useCallback(async (req: PlaceOrderRequest) => {
    client.setToken(token);
    const result = await client.placeOrder(req);
    if (onOrderPlaced) {
      onOrderPlaced(result);
    }
  }, [client, token, onOrderPlaced]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <TickerBar ticker={ticker} instrumentId={selectedInstrument} />
      <div style={{
        flex: 1, display: 'grid',
        gridTemplateColumns: '260px 1fr 300px',
        gap: 1, background: 'var(--border)', overflow: 'hidden',
      }}>
        {/* Left: Order Book */}
        <div style={{ background: 'var(--bg-primary)', display: 'flex', flexDirection: 'column' }}>
          <OrderBookView orderBook={orderBook} />
        </div>

        {/* Center: Chart + Recent Trades */}
        <div style={{
          background: 'var(--bg-primary)',
          display: 'flex', flexDirection: 'column',
        }}>
          {/* Real Candlestick Chart */}
          <div style={{
            flex: 1, minHeight: 300,
            borderBottom: '1px solid var(--border)',
          }}>
            <CandlestickChart instrumentId={selectedInstrument} />
          </div>

          {/* Recent Trades */}
          <div style={{ height: 240, overflow: 'hidden' }}>
            <RecentTrades trades={trades} instrumentId={selectedInstrument} />
          </div>
        </div>

        {/* Right: Order Entry */}
        <div style={{ background: 'var(--bg-primary)' }}>
          <OrderEntry
            instrumentId={selectedInstrument}
            bestBid={orderBook?.best_bid || null}
            bestAsk={orderBook?.best_ask || null}
            onSubmit={handleOrder}
          />
        </div>
      </div>
    </div>
  );
};
