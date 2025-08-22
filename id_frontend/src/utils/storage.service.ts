interface StorageData {
  [key: string]: any;
}

class StorageService {
  private prefix = 'id_app_';

  /**
   * Сохранение данных
   */
  set<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(this.prefix + key, serialized);
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  /**
   * Получение данных
   */
  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(this.prefix + key);
      if (item === null) return null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error('Failed to get from localStorage:', error);
      return null;
    }
  }

  /**
   * Удаление данных
   */
  remove(key: string): void {
    localStorage.removeItem(this.prefix + key);
  }

  /**
   * Очистка всех данных приложения
   */
  clear(): void {
    const keys = Object.keys(localStorage);
    keys.forEach((key) => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * Сохранение OAuth state для проверки
   */
  saveOAuthState(state: string, data: any): void {
    this.set(`oauth_state_${state}`, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Получение и удаление OAuth state
   */
  getAndRemoveOAuthState(state: string): any | null {
    const key = `oauth_state_${state}`;
    const stored = this.get<{ data: any; timestamp: number }>(key);
    
    if (!stored) return null;
    
    // Проверяем, что state не устарел (5 минут)
    if (Date.now() - stored.timestamp > 5 * 60 * 1000) {
      this.remove(key);
      return null;
    }
    
    this.remove(key);
    return stored.data;
  }

  /**
   * Сохранение PKCE verifier
   */
  savePKCEVerifier(state: string, verifier: string): void {
    this.set(`pkce_${state}`, {
      verifier,
      timestamp: Date.now(),
    });
  }

  /**
   * Получение PKCE verifier
   */
  getPKCEVerifier(state: string): string | null {
    const key = `pkce_${state}`;
    const stored = this.get<{ verifier: string; timestamp: number }>(key);
    
    if (!stored) return null;
    
    // Проверяем, что verifier не устарел (10 минут)
    if (Date.now() - stored.timestamp > 10 * 60 * 1000) {
      this.remove(key);
      return null;
    }
    
    this.remove(key);
    return stored.verifier;
  }
}

export const storageService = new StorageService();