/**
 * Herald Crypto Exchange - Candlestick Chart Component
 * Real candlestick chart using lightweight-charts with Binance kline data.
 */
import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import type { Kline } from '@herald/shared';
import { useApiClient } from '../../hooks/useApi';

interface Props {
  instrumentId: string;
}

type Interval = '1m' | '5m' | '15m' | '1h' | '4h' | '1d';

const INTERVALS: { label: string; value: Interval }[] = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1H', value: '1h' },
  { label: '4H', value: '4h' },
  { label: '1D', value: '1d' },
];

export const CandlestickChart: React.FC<Props> = ({ instrumentId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
  const client = useApiClient();
  const [interval, setInterval] = useState<Interval>('1h');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    // Clean up previous chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0b0e11' },
        textColor: '#848e9c',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#1e2329' },
        horzLines: { color: '#1e2329' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: '#3c4451', width: 1, style: 3, labelBackgroundColor: '#2b3139' },
        horzLine: { color: '#3c4451', width: 1, style: 3, labelBackgroundColor: '#2b3139' },
      },
      rightPriceScale: {
        borderColor: '#2b3139',
        scaleMargins: { top: 0.1, bottom: 0.2 },
      },
      timeScale: {
        borderColor: '#2b3139',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: { vertTouchDrag: false },
    });

    chartRef.current = chart;

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#0ecb81',
      downColor: '#f6465d',
      borderDownColor: '#f6465d',
      borderUpColor: '#0ecb81',
      wickDownColor: '#f6465d',
      wickUpColor: '#0ecb81',
    });

    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    // Fetch kline data
    setLoading(true);
    client.getKlines(instrumentId, interval, 200)
      .then((klines: Kline[]) => {
        if (!klines || klines.length === 0) return;

        const candleData = klines.map((k) => ({
          time: Math.floor(k.time / 1000) as import('lightweight-charts').UTCTimestamp,
          open: k.open,
          high: k.high,
          low: k.low,
          close: k.close,
        }));

        const volumeData = klines.map((k) => ({
          time: Math.floor(k.time / 1000) as import('lightweight-charts').UTCTimestamp,
          value: k.volume,
          color: k.close >= k.open ? 'rgba(14,203,129,0.3)' : 'rgba(246,70,93,0.3)',
        }));

        candleSeries.setData(candleData);
        volumeSeries.setData(volumeData);
        chart.timeScale().fitContent();
      })
      .catch(() => {})
      .finally(() => setLoading(false));

    // Resize observer
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        chart.applyOptions({ width, height });
      }
    });
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [instrumentId, interval, client]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Interval selector */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 2, padding: '6px 12px',
        borderBottom: '1px solid var(--border)', background: 'var(--bg-primary)',
      }}>
        {INTERVALS.map((i) => (
          <button
            key={i.value}
            onClick={() => setInterval(i.value)}
            style={{
              padding: '3px 10px', fontSize: 11, fontWeight: 500, cursor: 'pointer',
              border: 'none', borderRadius: 3,
              background: interval === i.value ? 'var(--bg-tertiary)' : 'transparent',
              color: interval === i.value ? 'var(--accent)' : 'var(--text-secondary)',
              transition: 'all 0.15s',
            }}
          >
            {i.label}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-tertiary)' }}>
          {instrumentId}
        </span>
      </div>
      {/* Chart container */}
      <div ref={containerRef} style={{ flex: 1, position: 'relative' }}>
        {loading && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            color: 'var(--text-tertiary)', fontSize: 13, zIndex: 10,
          }}>
            Loading chart...
          </div>
        )}
      </div>
    </div>
  );
};
