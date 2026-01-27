import '@testing-library/jest-dom'

// Declare global for TypeScript
declare global {
  var WebSocket: typeof WebSocket;
}

// Mock WebSocket for testing
if (typeof global !== 'undefined') {
  global.WebSocket = class WebSocket {
    constructor(public url: string) {}
    close() {}
    send() {}
    addEventListener() {}
    removeEventListener() {}
  } as any;
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})
