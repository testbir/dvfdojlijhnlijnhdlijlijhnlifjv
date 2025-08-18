// frontend/src/services/pointsService.ts

import { pointsApi } from "../api/pointsApi";

export interface PointsBalance {
  balance: number;
}

export interface PointsTransaction {
  id: number;
  user_id: number;
  amount: number;
  operation_type: 'award' | 'spend' | 'refund';
  description: string;
  reference_type?: string;
  reference_id?: number;
  created_at: string;
}

export interface TransactionsList {
  items: PointsTransaction[];
  total: number;
  limit: number;
  offset: number;
}

class PointsService {
  // Получение баланса
  async getBalance(): Promise<PointsBalance> {
    const response = await catalogApi.get("/v1/public/points/balance");
    return response.data;
  }

  // Получение истории транзакций
  async getTransactions(params?: {
    limit?: number;
    offset?: number;
  }): Promise<TransactionsList> {
    const response = await catalogApi.get("/v1/public/points/transactions", { params });
    return response.data;
  }
}

export default new PointsService();