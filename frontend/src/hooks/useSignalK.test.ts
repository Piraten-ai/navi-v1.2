import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSignalK } from './useSignalK';

describe('useSignalK', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        globalThis.fetch = vi.fn();
        vi.spyOn(console, 'warn').mockImplementation(() => {});
    });

    afterEach(() => {
        vi.restoreAllMocks();
        vi.useRealTimers();
    });

    it('should initialize with empty navData and disconnected state', () => {
        const { result } = renderHook(() => useSignalK());
        
        expect(result.current.navData).toEqual({});
        expect(result.current.connected).toBe(false);
    });

    it('should fetch navigation data successfully', async () => {
        const mockData = { speed: 10, heading: 180, depth: 20 };
        (globalThis.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => mockData,
        });

        const { result } = renderHook(() => useSignalK());

        await waitFor(() => {
            expect(result.current.connected).toBe(true);
            expect(result.current.navData).toEqual(mockData);
        });
    });

    it('should set connected to false on failed response', async () => {
        (globalThis.fetch as any).mockResolvedValueOnce({
            ok: false,
        });

        const { result } = renderHook(() => useSignalK());

        await waitFor(() => {
            expect(result.current.connected).toBe(false);
        });
    });

    it('should handle fetch errors gracefully', async () => {
        (globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'));

        const { result } = renderHook(() => useSignalK());

        await waitFor(() => {
            expect(result.current.connected).toBe(false);
            expect(console.warn).toHaveBeenCalledWith('SignalK connection failed:', expect.any(Error));
        });
    });

    it('should poll for updates every 1 second', async () => {
        const mockData = { speed: 10 };
        (globalThis.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => mockData,
        });

        renderHook(() => useSignalK());

        await waitFor(() => {
            expect(globalThis.fetch).toHaveBeenCalledTimes(1);
        });

        vi.advanceTimersByTime(1000);

        await waitFor(() => {
            expect(globalThis.fetch).toHaveBeenCalledTimes(2);
        });

        vi.advanceTimersByTime(1000);

        await waitFor(() => {
            expect(globalThis.fetch).toHaveBeenCalledTimes(3);
        });
    });

    it('should use VITE_SIGNALK_HOST environment variable', async () => {
        import.meta.env.VITE_SIGNALK_HOST = 'http://test-host:3000';
        
        (globalThis.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({}),
        });

        renderHook(() => useSignalK());

        await waitFor(() => {
            expect(globalThis.fetch).toHaveBeenCalledWith('http://test-host:3000/api/v1/navigation');
        });
    });

    it('should cleanup interval on unmount', async () => {
        const { unmount } = renderHook(() => useSignalK());
        
        const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval');
        
        unmount();

        expect(clearIntervalSpy).toHaveBeenCalled();
    });
});