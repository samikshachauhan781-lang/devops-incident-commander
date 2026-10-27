declare global {
  interface ImportMeta {
    readonly env: {
      readonly VITE_API_BASE_URL?: string;
      readonly DEV?: boolean;
    };
  }
}

export {};